from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.db.db import get_db
from .dashboard_service import DashboardServiceClass
from app.models.User import User
from app.dependency.dependencies import get_current_user
from app.core.logger import logger
from app.response.base import APIResponse
from app.response.dashboard_responses import DashboardResponse

router = APIRouter(prefix="", tags=["Dashboard"])

DashboardService = DashboardServiceClass()


@router.get(
    "/",
    response_model=APIResponse[DashboardResponse],
    status_code=status.HTTP_200_OK,
)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get aggregated dashboard data for the authenticated user.

    Returns counters (job descriptions, generated documents), a profile
    completeness summary, and the most recent jobs & documents.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        DashboardResponse: Aggregated dashboard payload

    Raises:
        HTTPException: If user not found or a database error occurs
    """
    try:
        logger.info(
            f"Dashboard request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        dashboard = DashboardService.get_dashboard(
            db=db, userId=str(current_user.id)
        )

        logger.info(
            f"Dashboard endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        return APIResponse(
            data=dashboard,
            message="Dashboard Fetched Successfully",
            status_code=200,
            success=True,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in dashboard retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in dashboard endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
