from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from app.models.User import User
from app.models.ApiKeys import ApiKey
from app.schema.ApiKeys import ApiKeyCreateRequest, ApiKeyUpdateRequest, ApiKeyResponse
from app.core.logger import logger
from app.validators.api_key_validators import ApiKeyValidator, ValidationException
from app.core.validation_error import ValidationErrorField, ValidationErrorResponse
from app.helpers.db_helpers import get_user_profile


class ApiKeysServiceClass:
    async def create_api_keys(
        self, db: Session, payload: ApiKeyCreateRequest, userId: str
    ) -> ApiKeyResponse:
        try:
            if not userId:
                logger.error(
                    "Api Key creation failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            try:
                logger.info(f"Validating Api Key creation payload for user {userId}")
                ApiKeyValidator.validate_provider(payload.provider)
                ApiKeyValidator.validate_api_base_url(payload.api_base_url)
                ApiKeyValidator.validate_api_version(payload.api_version)
                ApiKeyValidator.validate_is_active(payload.is_active)
                ApiKeyValidator.validate_key_name(payload.key_name)
                ApiKeyValidator.validate_key_value(payload.key_value)
                ApiKeyValidator.validate_expiry_format(payload.expires_at)

                logger.info(f"Payload validation successful for user {userId}")
            except ValidationException as validation_error:
                logger.warning(
                    f"Api Key payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "field": validation_error.field,
                        "code": validation_error.code,
                        "error": validation_error.message,
                    },
                )
                error_field = ValidationErrorField(
                    field=validation_error.field,
                    code=validation_error.code,
                    message=validation_error.message,
                    constraint=validation_error.constraint,
                )
                error_response = ValidationErrorResponse(
                    message="Please fix the validation errors below",
                    errors=[error_field],
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=error_response.model_dump(),
                )

            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Api Key creation failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            apiKey = ApiKey(
                provider=payload.provider,
                key_name=payload.key_name,
                key_value=payload.key_value,
                api_base_url=payload.api_base_url,
                api_version=payload.api_version,
                is_active=payload.is_active,
                expires_at=payload.expires_at,
            )

            db.add(apiKey)
            db.commit()
            db.refresh(apiKey)

            logger.info(
                f"Experience created successfully",
                extra={
                    "userId": userId,
                    "apiKeyId": apiKey.id,
                    "apiKeyName": apiKey.key_name,
                },
            )

            return ApiKeyResponse.model_validate(apiKey)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during api key creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e.orig),
                    "company": payload.company_name if payload else None,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database constraint violation occurred. This api key may already exist.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during experience creation for api key {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating api key.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during api key creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the api key.",
            )
