from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from uuid import UUID
from app.models.Project import Project
from app.models.Profile import Profile
from app.models.User import User
from app.schema.Project import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
)
from app.response.project_responses import (
    ProjectCreateResponse,
    ProjectGetResponse,
    ProjectUpdateResponse,
    ProjectListResponse,
)
from app.core.logger import logger
from app.validators.project_validators import ProjectValidator
from typing import List


class ProjectServiceClass:
    def create_project(
        self, db: Session, payload: ProjectCreateRequest, userId: str
    ) -> ProjectCreateResponse:
        """
        Create a new project for a user (profile must exist).

        Args:
            db: Database session
            payload: Project creation request data
            userId: User ID who owns the project

        Returns:
            ProjectCreateResponse: Created project data

        Raises:
            HTTPException: If validation fails, user not found, profile doesn't exist, or title duplicate
        """
        try:
            if not userId:
                logger.error(
                    f"Project creation failed: Missing user ID",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required",
                )

            try:
                logger.info(f"Validating project creation request for user: {userId}")
                ProjectValidator.validate_title(payload.title)
                ProjectValidator.validate_description(payload.description)
                ProjectValidator.validate_tech_stack(payload.techStack)
                ProjectValidator.validate_links(payload.links)
                ProjectValidator.validate_start_date(payload.startDate)
                ProjectValidator.validate_end_date(payload.endDate)
                ProjectValidator.validate_date_range(payload.startDate, payload.endDate)
            except ValueError as validation_error:
                logger.warning(
                    f"Project validation failed for user {userId}: {str(validation_error)}",
                    extra={"userId": userId, "error": str(validation_error)},
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation error: {str(validation_error)}",
                )

            logger.debug(f"Checking if user exists: {userId}")
            user = db.query(User).filter(User.id == userId).first()
            if not user:
                logger.warning(
                    f"Project creation failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )

            logger.debug(f"Checking if profile exists for user: {userId}")
            user_profile = db.query(Profile).filter(Profile.userId == user.id).first()

            if not user_profile:
                logger.warning(
                    f"Project creation failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist. Please create a profile first before adding projects.",
                )

            logger.info(
                f"Creating new project for user: {userId}",
                extra={"userId": userId, "profileId": str(user_profile.id)},
            )
            project = Project(
                title=payload.title,
                description=payload.description,
                profileId=user_profile.id,
                techStack=payload.techStack,
                links=payload.links,
                startDate=payload.startDate,
                endDate=payload.endDate,
            )

            db.add(project)
            db.commit()
            db.refresh(project)

            logger.info(
                f"Project created successfully for user: {userId}",
                extra={"userId": userId, "projectId": str(project.id)},
            )

            return ProjectCreateResponse.model_validate(project)

        except HTTPException:
            raise
        except IntegrityError as e:
            db.rollback()
            if "title" in str(e.orig).lower():
                logger.warning(
                    f"Unique constraint violation: Project title already exists",
                    extra={"userId": userId, "title": payload.title},
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Project title already exists. Please use a different title.",
                )
            logger.error(
                f"Integrity error during project creation for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e.orig)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during project creation for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating project",
            )
        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during project creation for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating project",
            )

    def get_project(
        self, db: Session, userId: str, projectId: str
    ) -> ProjectGetResponse:
        """
        Get a specific project for a user.

        Args:
            db: Database session
            userId: User ID who owns the project
            projectId: Project ID to retrieve

        Returns:
            ProjectGetResponse: Project data

        Raises:
            HTTPException: If user/profile/project not found
        """
        try:
            if not userId:
                logger.error(
                    f"Project retrieval failed: Missing user ID",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required",
                )

            logger.debug(f"Checking if user exists: {userId}")
            user = db.query(User).filter(User.id == userId).first()
            if not user:
                logger.warning(
                    f"Project retrieval failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )

            logger.debug(f"Checking if profile exists for user: {userId}")
            user_profile = db.query(Profile).filter(Profile.userId == user.id).first()

            if not user_profile:
                logger.warning(
                    f"Project retrieval failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist",
                )

            logger.debug(f"Retrieving project {projectId} for user: {userId}")
            project = (
                db.query(Project)
                .filter(
                    Project.id == projectId,
                    Project.profileId == user_profile.id,
                )
                .first()
            )

            if not project:
                logger.warning(
                    f"Project retrieval failed: Project not found",
                    extra={"userId": userId, "projectId": projectId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found",
                )

            logger.info(
                f"Project retrieved successfully for user: {userId}",
                extra={"userId": userId, "projectId": str(project.id)},
            )

            return ProjectGetResponse.model_validate(project)

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during project retrieval for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving project",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error during project retrieval for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving project",
            )

    def list_projects(self, db: Session, userId: str) -> List[ProjectListResponse]:
        """
        Get all projects for a user.

        Args:
            db: Database session
            userId: User ID whose projects to retrieve

        Returns:
            List[ProjectListResponse]: List of user's projects

        Raises:
            HTTPException: If user/profile not found
        """
        try:
            if not userId:
                logger.error(
                    f"Project list retrieval failed: Missing user ID",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required",
                )

            logger.debug(f"Checking if user exists: {userId}")
            user = db.query(User).filter(User.id == userId).first()
            if not user:
                logger.warning(
                    f"Project list retrieval failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )

            logger.debug(f"Checking if profile exists for user: {userId}")
            user_profile = db.query(Profile).filter(Profile.userId == user.id).first()

            if not user_profile:
                logger.warning(
                    f"Project list retrieval failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist",
                )

            logger.debug(f"Retrieving all projects for user: {userId}")
            projects = (
                db.query(Project).filter(Project.profileId == user_profile.id).all()
            )

            logger.info(
                f"Retrieved {len(projects)} projects for user: {userId}",
                extra={"userId": userId, "projectCount": len(projects)},
            )

            return [ProjectListResponse.model_validate(project) for project in projects]

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during project list retrieval for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving projects",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error during project list retrieval for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving projects",
            )

    def update_project(
        self, db: Session, userId: str, projectId: str, payload: ProjectUpdateRequest
    ) -> ProjectUpdateResponse:
        """
        Update an existing project for a user.

        Args:
            db: Database session
            userId: User ID who owns the project
            projectId: Project ID to update
            payload: Project update request data

        Returns:
            ProjectUpdateResponse: Updated project data

        Raises:
            HTTPException: If validation fails or project not found
        """
        try:
            if not userId:
                logger.error(
                    f"Project update failed: Missing user ID",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required",
                )

            try:
                logger.info(f"Validating project update request for user: {userId}")
                if payload.title is not None:
                    ProjectValidator.validate_title(payload.title)
                if payload.description is not None:
                    ProjectValidator.validate_description(payload.description)
                if payload.techStack is not None:
                    ProjectValidator.validate_tech_stack(payload.techStack)
                if payload.links is not None:
                    ProjectValidator.validate_links(payload.links)
                if payload.startDate is not None:
                    ProjectValidator.validate_start_date(payload.startDate)
                if payload.endDate is not None:
                    ProjectValidator.validate_end_date(payload.endDate)
                ProjectValidator.validate_date_range(payload.startDate, payload.endDate)
            except ValueError as validation_error:
                logger.warning(
                    f"Project update validation failed for user {userId}: {str(validation_error)}",
                    extra={"userId": userId, "error": str(validation_error)},
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation error: {str(validation_error)}",
                )

            logger.debug(f"Checking if user exists: {userId}")
            user = db.query(User).filter(User.id == userId).first()
            if not user:
                logger.warning(
                    f"Project update failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )

            logger.debug(f"Checking if profile exists for user: {userId}")
            user_profile = db.query(Profile).filter(Profile.userId == user.id).first()

            if not user_profile:
                logger.warning(
                    f"Project update failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist",
                )

            logger.debug(f"Retrieving project {projectId} for update")
            project = (
                db.query(Project)
                .filter(
                    Project.id == projectId,
                    Project.profileId == user_profile.id,
                )
                .first()
            )

            if not project:
                logger.warning(
                    f"Project update failed: Project not found",
                    extra={"userId": userId, "projectId": projectId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found",
                )

            logger.info(
                f"Updating project {projectId} for user: {userId}",
                extra={"userId": userId, "projectId": projectId},
            )

            if payload.title is not None:
                project.title = payload.title
            if payload.description is not None:
                project.description = payload.description
            if payload.techStack is not None:
                project.techStack = payload.techStack
            if payload.links is not None:
                project.links = payload.links
            if payload.startDate is not None:
                project.startDate = payload.startDate
            if payload.endDate is not None:
                project.endDate = payload.endDate

            db.commit()
            db.refresh(project)

            logger.info(
                f"Project updated successfully for user: {userId}",
                extra={"userId": userId, "projectId": str(project.id)},
            )

            return ProjectUpdateResponse.model_validate(project)

        except HTTPException:
            raise
        except IntegrityError as e:
            db.rollback()
            if "title" in str(e.orig).lower():
                logger.warning(
                    f"Unique constraint violation: Project title already exists",
                    extra={"userId": userId, "projectId": projectId},
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Project title already exists. Please use a different title.",
                )
            logger.error(
                f"Integrity error during project update for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e.orig)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred",
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during project update for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating project",
            )
        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during project update for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating project",
            )

    def delete_project(self, db: Session, userId: str, projectId: str) -> dict:
        """
        Delete a project for a user.

        Args:
            db: Database session
            userId: User ID who owns the project
            projectId: Project ID to delete

        Returns:
            dict: Deletion confirmation

        Raises:
            HTTPException: If project not found
        """
        try:
            if not userId:
                logger.error(
                    f"Project deletion failed: Missing user ID",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID is required",
                )

            logger.debug(f"Checking if user exists: {userId}")
            user = db.query(User).filter(User.id == userId).first()
            if not user:
                logger.warning(
                    f"Project deletion failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist",
                )

            logger.debug(f"Checking if profile exists for user: {userId}")
            user_profile = db.query(Profile).filter(Profile.userId == user.id).first()

            if not user_profile:
                logger.warning(
                    f"Project deletion failed: User profile not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile does not exist",
                )

            logger.debug(f"Retrieving project {projectId} for deletion")
            project = (
                db.query(Project)
                .filter(
                    Project.id == projectId,
                    Project.profileId == user_profile.id,
                )
                .first()
            )

            if not project:
                logger.warning(
                    f"Project deletion failed: Project not found",
                    extra={"userId": userId, "projectId": projectId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found",
                )

            project_id = project.id
            project_title = project.title

            logger.info(
                f"Deleting project {projectId} for user: {userId}",
                extra={"userId": userId, "projectId": projectId},
            )
            db.delete(project)
            db.commit()

            logger.info(
                f"Project deleted successfully for user: {userId}",
                extra={"userId": userId, "projectId": str(project_id)},
            )

            return {
                "message": f"Project '{project_title}' has been successfully deleted",
                "id": str(project_id),
                "title": project_title,
            }

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during project deletion for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while deleting project",
            )
        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during project deletion for user {userId}: {str(e)}",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting project",
            )


ProjectService = ProjectServiceClass()
