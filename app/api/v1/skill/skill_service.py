from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from app.models.User import User
from app.models.Skill import Skill
from app.models.UserSkill import UserSkill
from app.schema.Skill import SkillCreateRequest, SkillUpdateRequest
from app.response.skill_responses import (
    SkillCreateResponse,
    SkillGetResponse,
    SkillListResponse,
    SkillUpdateResponse,
)
from app.core.logger import logger
from app.validators.skill_validators import SkillValidator


class SkillServiceClass:
    def create_skill(
        self, db: Session, payload: SkillCreateRequest, userId
    ) -> SkillCreateResponse:
        """
        Create a new skill in the system for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Validate the request payload
        3. Verify user exists in database
        4. Check if skill name already exists (unique constraint)
        5. Create and save the skill record with current user as creator

        Args:
            db: Database session
            payload: SkillCreateRequest with skill details
            userId: Authenticated user's ID (creator)

        Returns:
            SkillCreateResponse with created skill details

        Raises:
            HTTPException: For various validation, authentication, or database errors
        """
        try:
            logger.info(f"Starting skill creation process for user: {userId}")

            if not userId:
                logger.error(
                    "Skill creation failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            try:
                logger.info(f"Validating skill creation payload for user {userId}")
                validated_name = SkillValidator.validate_name(payload.name)
                validated_name = SkillValidator.validate_name_format(validated_name)
                logger.info(f"Payload validation successful for user {userId}")
            except ValueError as validation_error:
                logger.warning(
                    f"Skill payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "error": str(validation_error),
                        "skillName": payload.name,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation error: {str(validation_error)}",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Skill creation failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Checking if skill name already exists: {validated_name}")
            existing_skill = db.query(Skill).filter(
                Skill.name.ilike(validated_name)
            ).first()

            if existing_skill:
                logger.warning(
                    f"Skill creation failed: Skill name already exists",
                    extra={
                        "userId": userId,
                        "skillName": validated_name,
                        "existingSkillId": existing_skill.id,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Skill '{validated_name}' already exists. Skill names must be unique.",
                )

            logger.info(
                f"Creating skill record for user {userId} with name: {validated_name}"
            )

            skill = Skill(
                name=validated_name,
                created_by=userId,
            )

            db.add(skill)
            db.commit()
            db.refresh(skill)

            logger.info(
                f"Skill record created successfully",
                extra={
                    "userId": userId,
                    "skillId": skill.id,
                    "skillName": skill.name,
                },
            )

            return SkillCreateResponse.model_validate(skill)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during skill creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e.orig),
                    "skillName": payload.name if payload else None,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Skill name already exists. Skill names must be unique.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during skill creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating skill.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during skill creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the skill.",
            )

    def list_skills(self, db: Session, userId: str = None) -> list[SkillListResponse]:
        """
        Retrieve all skills in the system or user's skills.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Fetch all skills or user's skills based on parameters
        4. Return skills as response objects

        Args:
            db: Database session
            userId: Optional authenticated user's ID (if provided, returns user's skills)

        Returns:
            List of SkillListResponse objects with skill details

        Raises:
            HTTPException: For authentication or database errors
        """
        try:
            if userId:
                logger.info(f"Starting user skill retrieval process for user: {userId}")

                if not userId:
                    logger.error(
                        "Skill retrieval failed: No user ID provided (authentication missing)"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required: User ID is missing",
                    )

                logger.info(f"Verifying user exists with ID: {userId}")
                user = db.query(User).filter(User.id == userId).first()

                if not user:
                    logger.warning(
                        f"Skill retrieval failed: User not found",
                        extra={"userId": userId},
                    )
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User does not exist. Invalid user ID.",
                    )

                logger.info(f"User verified successfully: {userId}")

                logger.info(f"Fetching user's skills for user: {userId}")

                user_skills = (
                    db.query(Skill)
                    .join(UserSkill, Skill.id == UserSkill.skillId)
                    .filter(UserSkill.userId == userId)
                    .all()
                )

                logger.info(
                    f"Successfully retrieved user skills",
                    extra={
                        "userId": userId,
                        "skillCount": len(user_skills),
                    },
                )

                return [SkillListResponse.model_validate(skill) for skill in user_skills]
            else:
                logger.info(f"Fetching all available skills")

                skills = db.query(Skill).all()

                logger.info(
                    f"Successfully retrieved all skills",
                    extra={
                        "skillCount": len(skills),
                    },
                )

                return [SkillListResponse.model_validate(skill) for skill in skills]

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            logger.error(
                f"Database error during skill retrieval",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving skills.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during skill retrieval",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving skills.",
            )

    def get_skill(self, db: Session, skillId: str) -> SkillGetResponse:
        """
        Retrieve a specific skill by ID.

        Steps:
        1. Verify skill ID is provided
        2. Fetch the specific skill by skillId
        3. Verify skill exists
        4. Return skill as response object

        Args:
            db: Database session
            skillId: Skill ID to retrieve

        Returns:
            SkillGetResponse object with skill details

        Raises:
            HTTPException: For validation or database errors
        """
        try:
            logger.info(
                f"Starting skill retrieval process",
                extra={"skillId": skillId},
            )

            if not skillId:
                logger.error(
                    "Skill retrieval failed: No skill ID provided",
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Skill ID is required",
                )

            logger.info(
                f"Fetching skill from database",
                extra={
                    "skillId": skillId,
                },
            )

            skill = db.query(Skill).filter(Skill.id == skillId).first()

            if not skill:
                logger.warning(
                    f"Skill retrieval failed: Skill not found",
                    extra={
                        "skillId": skillId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Skill not found.",
                )

            logger.info(
                f"Successfully retrieved skill",
                extra={
                    "skillId": skill.id,
                    "skillName": skill.name,
                },
            )

            return SkillGetResponse.model_validate(skill)

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            logger.error(
                f"Database error during skill retrieval",
                extra={
                    "skillId": skillId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving skill.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during skill retrieval",
                extra={
                    "skillId": skillId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving skill.",
            )

    def update_skill(
        self,
        db: Session,
        skillId: str,
        payload: SkillUpdateRequest,
        userId: str,
    ) -> SkillUpdateResponse:
        """
        Update an existing skill (only creator can update).

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify skill exists
        4. Verify user is the creator of the skill
        5. Validate the request payload
        6. Update the skill fields
        7. Save changes and return updated skill

        Args:
            db: Database session
            skillId: Skill ID to update
            payload: SkillUpdateRequest with fields to update
            userId: Authenticated user's ID (must be creator)

        Returns:
            SkillUpdateResponse object with updated skill details

        Raises:
            HTTPException: For authentication, authorization, validation, or database errors
        """
        try:
            logger.info(
                f"Starting skill update process",
                extra={"userId": userId, "skillId": skillId},
            )

            if not userId:
                logger.error(
                    "Skill update failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not skillId:
                logger.error(
                    "Skill update failed: No skill ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Skill ID is required",
                )

            try:
                logger.info(f"Validating skill update payload for user {userId}")
                validated_name = SkillValidator.validate_name(payload.name)
                validated_name = SkillValidator.validate_name_format(validated_name)
                logger.info(f"Payload validation successful for user {userId}")
            except ValueError as validation_error:
                logger.warning(
                    f"Skill payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "skillId": skillId,
                        "error": str(validation_error),
                        "skillName": payload.name,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation error: {str(validation_error)}",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Skill update failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(
                f"Fetching skill from database",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                },
            )

            skill = db.query(Skill).filter(Skill.id == skillId).first()

            if not skill:
                logger.warning(
                    f"Skill update failed: Skill not found",
                    extra={
                        "userId": userId,
                        "skillId": skillId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Skill not found.",
                )

            logger.info(f"Skill found, verifying authorization for user {userId}")

            if str(skill.created_by) != str(userId):
                logger.warning(
                    f"Skill update failed: User is not the creator",
                    extra={
                        "userId": userId,
                        "skillId": skillId,
                        "skillCreator": skill.created_by,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the skill creator can update this skill.",
                )

            logger.info(f"Authorization verified, proceeding with update for {skillId}")

            logger.info(f"Checking if new skill name already exists: {validated_name}")
            existing_skill = (
                db.query(Skill)
                .filter(
                    Skill.name.ilike(validated_name),
                    Skill.id != skillId,
                )
                .first()
            )

            if existing_skill:
                logger.warning(
                    f"Skill update failed: Skill name already exists",
                    extra={
                        "userId": userId,
                        "skillId": skillId,
                        "newSkillName": validated_name,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Skill '{validated_name}' already exists. Skill names must be unique.",
                )

            logger.info(f"Updating skill fields for {skillId}")
            updated_fields = {}

            if payload.name is not None:
                skill.name = validated_name
                updated_fields["name"] = validated_name

            if not updated_fields:
                logger.warning(
                    f"No fields provided for update",
                    extra={
                        "userId": userId,
                        "skillId": skillId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided for update",
                )

            logger.info(
                f"Saving skill updates to database",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                    "updatedFields": list(updated_fields.keys()),
                },
            )

            db.commit()
            db.refresh(skill)

            logger.info(
                f"Skill updated successfully",
                extra={
                    "userId": userId,
                    "skillId": skill.id,
                    "skillName": skill.name,
                    "updatedFields": list(updated_fields.keys()),
                },
            )

            return SkillUpdateResponse.model_validate(skill)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during skill update for user {userId}",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                    "error": str(e.orig),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Skill name already exists. Skill names must be unique.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during skill update for user {userId}",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating skill.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during skill update for user {userId}",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating skill.",
            )

    def delete_skill(self, db: Session, skillId: str, userId: str) -> dict:
        """
        Delete a specific skill (only creator can delete).

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Fetch the specific skill by skillId
        4. Verify skill exists
        5. Verify user is the creator of the skill
        6. Delete the skill from database
        7. Return success response with deleted skill details

        Args:
            db: Database session
            skillId: Skill ID to delete
            userId: Authenticated user's ID (must be creator)

        Returns:
            dict with success message and deleted skill ID

        Raises:
            HTTPException: For authentication, authorization, or database errors
        """
        try:
            logger.info(
                f"Starting skill deletion process",
                extra={"userId": userId, "skillId": skillId},
            )

            if not userId:
                logger.error(
                    "Skill deletion failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not skillId:
                logger.error(
                    "Skill deletion failed: No skill ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Skill ID is required",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Skill deletion failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(
                f"Fetching skill from database for deletion",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                },
            )

            skill = db.query(Skill).filter(Skill.id == skillId).first()

            if not skill:
                logger.warning(
                    f"Skill deletion failed: Skill not found",
                    extra={
                        "userId": userId,
                        "skillId": skillId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Skill not found.",
                )

            logger.info(f"Skill found, verifying authorization for user {userId}")

            if str(skill.created_by) != str(userId):
                logger.warning(
                    f"Skill deletion failed: User is not the creator",
                    extra={
                        "userId": userId,
                        "skillId": skillId,
                        "skillCreator": skill.created_by,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the skill creator can delete this skill.",
                )

            deleted_skill_id = skill.id
            deleted_skill_name = skill.name

            logger.info(
                f"Skill found, proceeding with deletion",
                extra={
                    "userId": userId,
                    "skillId": deleted_skill_id,
                    "skillName": deleted_skill_name,
                },
            )

            logger.info(
                f"Deleting skill from database",
                extra={
                    "userId": userId,
                    "skillId": deleted_skill_id,
                },
            )

            db.delete(skill)
            db.commit()

            logger.info(
                f"Skill deleted successfully",
                extra={
                    "userId": userId,
                    "skillId": deleted_skill_id,
                    "skillName": deleted_skill_name,
                },
            )

            return {
                "success": True,
                "message": "Skill deleted successfully",
                "deletedSkillId": str(deleted_skill_id),
                "skillName": deleted_skill_name,
            }

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during skill deletion for user {userId}",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while deleting skill.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during skill deletion for user {userId}",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting skill.",
            )

    def add_skill_to_user(
        self, db: Session, userId: str, skillId: str
    ) -> dict:
        """
        Add a skill to a user's profile.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify skill exists
        4. Check if user already has this skill
        5. Create UserSkill record linking user and skill

        Args:
            db: Database session
            userId: Authenticated user's ID
            skillId: Skill ID to add

        Returns:
            dict with success message and skill details

        Raises:
            HTTPException: For validation, authentication, or database errors
        """
        try:
            logger.info(
                f"Starting skill addition process",
                extra={"userId": userId, "skillId": skillId},
            )

            if not userId:
                logger.error(
                    "Skill addition failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Skill addition failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Verifying skill exists with ID: {skillId}")
            skill = db.query(Skill).filter(Skill.id == skillId).first()

            if not skill:
                logger.warning(
                    f"Skill addition failed: Skill not found",
                    extra={"userId": userId, "skillId": skillId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Skill not found.",
                )

            logger.info(f"Skill verified successfully: {skillId}")

            logger.info(f"Checking if user already has this skill")
            existing_user_skill = (
                db.query(UserSkill)
                .filter(
                    UserSkill.userId == userId,
                    UserSkill.skillId == skillId,
                )
                .first()
            )

            if existing_user_skill:
                logger.warning(
                    f"Skill addition failed: User already has this skill",
                    extra={"userId": userId, "skillId": skillId},
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already has this skill.",
                )

            logger.info(f"Adding skill to user")
            user_skill = UserSkill(userId=userId, skillId=skillId)

            db.add(user_skill)
            db.commit()
            db.refresh(user_skill)

            logger.info(
                f"Skill added to user successfully",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                    "skillName": skill.name,
                },
            )

            return {
                "success": True,
                "message": "Skill added to user profile successfully",
                "skillId": str(skillId),
                "skillName": skill.name,
            }

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during skill addition for user {userId}",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while adding skill to user.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during skill addition for user {userId}",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while adding skill to user.",
            )

    def remove_skill_from_user(
        self, db: Session, userId: str, skillId: str
    ) -> dict:
        """
        Remove a skill from a user's profile.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Fetch the UserSkill record
        4. Verify record exists
        5. Delete the UserSkill record

        Args:
            db: Database session
            userId: Authenticated user's ID
            skillId: Skill ID to remove

        Returns:
            dict with success message

        Raises:
            HTTPException: For authentication or database errors
        """
        try:
            logger.info(
                f"Starting skill removal process",
                extra={"userId": userId, "skillId": skillId},
            )

            if not userId:
                logger.error(
                    "Skill removal failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Skill removal failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Fetching UserSkill record from database")
            user_skill = (
                db.query(UserSkill)
                .filter(
                    UserSkill.userId == userId,
                    UserSkill.skillId == skillId,
                )
                .first()
            )

            if not user_skill:
                logger.warning(
                    f"Skill removal failed: User does not have this skill",
                    extra={"userId": userId, "skillId": skillId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not have this skill.",
                )

            logger.info(f"Removing skill from user")
            db.delete(user_skill)
            db.commit()

            logger.info(
                f"Skill removed from user successfully",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                },
            )

            return {
                "success": True,
                "message": "Skill removed from user profile successfully",
                "skillId": str(skillId),
            }

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during skill removal for user {userId}",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while removing skill from user.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during skill removal for user {userId}",
                extra={
                    "userId": userId,
                    "skillId": skillId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while removing skill from user.",
            )
