from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from app.models.Profile import Profile
from app.models.Experience import Experience
from app.schema.Experience import ExperienceCreateRequest, ExperienceUpdateRequest
from app.response.experience_responses import (
    ExperienceCreateResponse,
    ExperienceGetResponse,
    ExperienceListResponse,
    ExperienceUpdateResponse,
)
from app.core.logger import logger
from app.validators.experience_validators import ExperienceValidator


class ExperienceServiceClass:
    pass
