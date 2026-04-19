from fastapi import APIRouter, Depends
from .health_service import health_service, HealthService

router = APIRouter()


@router.get("/")
def get_health(
    service: HealthService = Depends(lambda: health_service),
):
    return service.get_health()
