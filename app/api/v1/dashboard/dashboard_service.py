from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.models.User import User
from app.models.Profile import Profile
from app.models.Project import Project
from app.models.Experience import Experience
from app.models.Publication import Publication
from app.models.Academic import Academic
from app.models.UserSkill import UserSkill
from app.models.UserTool import UserTool
from app.models.JobDescription import JobDescription
from app.models.GeneratedDocument import (
    GeneratedDocumment,
    GeneratedDocumentEnumType,
    GeneratedDocumentStatusEnumType,
)
from app.response.dashboard_responses import (
    DashboardResponse,
    DashboardStats,
    ProfileSummary,
    RecentJob,
    RecentDocument,
)
from app.core.logger import logger


class DashboardServiceClass:
    def get_dashboard(self, db: Session, userId: str) -> DashboardResponse:
        """
        Build the aggregated dashboard payload for an authenticated user.

        Steps:
        1. Verify user authentication and existence
        2. Count job descriptions and generated documents (by type & status)
        3. Summarise the user's profile (counts of related entities)
        4. Collect the most recent job descriptions and documents

        Args:
            db: Database session
            userId: Authenticated user's ID

        Returns:
            DashboardResponse with stats, profile summary and recent activity

        Raises:
            HTTPException: For authentication or database errors
        """
        try:
            logger.info(
                "Starting dashboard aggregation",
                extra={"userId": userId},
            )

            if not userId:
                logger.error("Dashboard failed: No user ID provided")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            user = db.query(User).filter(User.id == userId).first()
            if not user:
                logger.warning(
                    "Dashboard failed: User not found", extra={"userId": userId}
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            # ----- Job descriptions -----
            total_job_descriptions = (
                db.query(JobDescription)
                .filter(JobDescription.userId == userId)
                .count()
            )

            # ----- Generated documents -----
            documents_query = db.query(GeneratedDocumment).filter(
                GeneratedDocumment.userId == userId
            )
            total_documents = documents_query.count()
            total_resumes = documents_query.filter(
                GeneratedDocumment.gen_doc_type == GeneratedDocumentEnumType.RESUME
            ).count()
            total_cover_letters = documents_query.filter(
                GeneratedDocumment.gen_doc_type
                == GeneratedDocumentEnumType.COVER_LETTER
            ).count()
            completed_documents = documents_query.filter(
                GeneratedDocumment.status
                == GeneratedDocumentStatusEnumType.Completed
            ).count()
            pending_documents = documents_query.filter(
                GeneratedDocumment.status.in_(
                    [
                        GeneratedDocumentStatusEnumType.Pending,
                        GeneratedDocumentStatusEnumType.Processing,
                    ]
                )
            ).count()
            failed_documents = documents_query.filter(
                GeneratedDocumment.status == GeneratedDocumentStatusEnumType.failed
            ).count()

            stats = DashboardStats(
                totalJobDescriptions=total_job_descriptions,
                totalDocuments=total_documents,
                totalResumes=total_resumes,
                totalCoverLetters=total_cover_letters,
                completedDocuments=completed_documents,
                pendingDocuments=pending_documents,
                failedDocuments=failed_documents,
            )

            # ----- Profile summary -----
            profile = db.query(Profile).filter(Profile.userId == userId).first()

            total_skills = (
                db.query(UserSkill).filter(UserSkill.userId == userId).count()
            )
            total_tools = (
                db.query(UserTool).filter(UserTool.userId == userId).count()
            )

            if profile:
                total_projects = (
                    db.query(Project)
                    .filter(Project.profileId == profile.id)
                    .count()
                )
                total_experiences = (
                    db.query(Experience)
                    .filter(Experience.profileId == profile.id)
                    .count()
                )
                total_publications = (
                    db.query(Publication)
                    .filter(Publication.profileId == profile.id)
                    .count()
                )
                total_academics = (
                    db.query(Academic)
                    .filter(Academic.profileId == profile.id)
                    .count()
                )
                profile_summary = ProfileSummary(
                    fullName=profile.full_name,
                    headline=profile.headline,
                    isOnboarded=bool(profile.isOnboarded),
                    totalProjects=total_projects,
                    totalExperiences=total_experiences,
                    totalSkills=total_skills,
                    totalTools=total_tools,
                    totalPublications=total_publications,
                    totalAcademics=total_academics,
                )
            else:
                profile_summary = ProfileSummary(
                    fullName=None,
                    headline=None,
                    isOnboarded=False,
                    totalProjects=0,
                    totalExperiences=0,
                    totalSkills=total_skills,
                    totalTools=total_tools,
                    totalPublications=0,
                    totalAcademics=0,
                )

            # ----- Recent job descriptions -----
            recent_jobs_rows = (
                db.query(JobDescription)
                .filter(JobDescription.userId == userId)
                .order_by(JobDescription.Created_At.desc())
                .limit(5)
                .all()
            )
            recent_jobs = [
                RecentJob(
                    id=job.id,
                    roleName=job.Role_Name,
                    company=job.Company,
                    roleType=job.Role_Type.value if job.Role_Type else None,
                    location=job.Location.value if job.Location else None,
                    createdAt=job.Created_At,
                )
                for job in recent_jobs_rows
            ]

            # ----- Recent generated documents -----
            recent_docs_rows = (
                db.query(GeneratedDocumment)
                .filter(GeneratedDocumment.userId == userId)
                .order_by(GeneratedDocumment.created_at.desc())
                .limit(5)
                .all()
            )
            recent_documents = [
                RecentDocument(
                    id=doc.id,
                    type=doc.gen_doc_type.value if doc.gen_doc_type else "Resume",
                    status=doc.status.value if doc.status else "pending",
                    createdAt=doc.created_at,
                )
                for doc in recent_docs_rows
            ]

            logger.info(
                "Dashboard aggregation completed successfully",
                extra={
                    "userId": userId,
                    "totalJobDescriptions": total_job_descriptions,
                    "totalDocuments": total_documents,
                },
            )

            return DashboardResponse(
                stats=stats,
                profile=profile_summary,
                recentJobs=recent_jobs,
                recentDocuments=recent_documents,
            )

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            logger.error(
                "Database error during dashboard aggregation",
                extra={"userId": userId, "error": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while building the dashboard.",
            )

        except Exception as e:
            logger.error(
                "Unexpected error during dashboard aggregation",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while building the dashboard.",
            )
