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
from app.helpers.api_key_encryption import api_key_encryption


class ApiKeysServiceClass:
    async def get_decrypted_key_for_use(
        self, db: Session, key_id: str, user_id: str
    ) -> str:
        """Retrieve and decrypt API key for making API calls"""
        api_key = (
            db.query(ApiKey)
            .filter(
                ApiKey.id == key_id, ApiKey.user_id == user_id, ApiKey.is_active == True
            )
            .first()
        )

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Active API key not found"
            )

        decrypted_key = api_key_encryption.decrypt_api_key(api_key.key_value)
        return decrypted_key

    async def test_api_key(self, provider: str, api_key: str) -> bool:
        """Test if the API key works with the provider"""
        try:
            if provider == "groq":
                from groq import Groq

                client = Groq(api_key=api_key)
                # Make a minimal test call (e.g., list models)
                client.models.list()
            elif provider == "anthropic":
                # from anthropic import Anthropic

                # client = Anthropic(api_key=api_key)
                # Test with a minimal API call
                pass
            # Add other providers...
            return True
        except Exception as e:
            logger.warning(f"API key test failed for {provider}: {str(e)}")
            raise ValidationException(
                field="key_value",
                code="invalid_key",
                message=f"Invalid {provider} API key. Please check your key and try again.",
                constraint="valid_api_key",
            )

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
                ApiKeyValidator.validate_expiry_format(payload.expires_at)

                ApiKeyValidator.validate_key_value(payload.key_value, payload.provider)

                await self.test_api_key(payload.provider, payload.key_value)

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

            encrypted_key = api_key_encryption.encrypt_api_key(payload.key_value)

            masked_key = ApiKeyValidator.sanitize_key_value_for_logging(
                payload.key_value
            )
            logger.debug(
                f"Storing API key: {masked_key} for provider: {payload.provider}"
            )

            apiKey = ApiKey(
                provider=payload.provider,
                key_name=payload.key_name,
                key_value=encrypted_key,
                api_base_url=payload.api_base_url,
                api_version=payload.api_version,
                is_active=payload.is_active,
                expires_at=payload.expires_at,
                user_id=userId,
            )

            db.add(apiKey)
            db.commit()
            db.refresh(apiKey)

            response = ApiKeyResponse.model_validate(apiKey)
            response.key_value = "••••••••"

            logger.info(f"API key created successfully for user {userId}")
            return response

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

    async def get_api_keys(self, db: Session, userId: str) -> list[ApiKeyResponse]:
        try:
            if not userId:
                logger.error(
                    "Api Key creation failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
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

            api_keys = db.query(ApiKey).filter(
                ApiKey.user_id == userId, ApiKey.is_active == True
            )

            return [ApiKeyResponse.model_validate(api_key) for api_key in api_keys]

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during api key fetch for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e.orig),
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
                f"Database error during api keys fetch for api key {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching api key.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during fetching api key for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while api key",
            )

    async def get_api_key(self, db: Session, userId: str, keyId: str) -> ApiKeyResponse:
        try:
            if not userId:
                logger.error(
                    "Api Key creation failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
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

            api_key = db.query(ApiKey).filter(
                ApiKey.id == keyId, ApiKey.user_id == userId, ApiKey.is_active == True
            )

            return ApiKeyResponse.model_validate(api_key)
        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during api key fetch for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e.orig),
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
                f"Database error during api keys fetch for api key {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching api key.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during fetching api key for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while api key",
            )

    async def update_api_key(
        self,
        db: Session,
        userId: str,
        keyId: str,
        payload: ApiKeyUpdateRequest,
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

            if not keyId:
                logger.error(
                    "Api Key update failed: No api key ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Api Key ID is required",
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

            try:
                logger.info(
                    f"Validating api key update payload for update api key {userId}"
                )
                if payload.api_base_url is not None:
                    ApiKeyValidator.validate_api_base_url(payload.api_base_url)
                if payload.api_version is not None:
                    ApiKeyValidator.validate_api_version(payload.api_version)
                if payload.key_name is not None:
                    ApiKeyValidator.validate_key_name(payload.key_name)
                if payload.key_value is not None:
                    ApiKeyValidator.validate_key_value(payload.key_value)
                if payload.is_active is not None:
                    ApiKeyValidator.validate_is_active(payload.is_active)
                if payload.expires_at is not None:
                    ApiKeyValidator.validate_expiry_format(payload.expires_at)
                if payload.provider is not None:
                    ApiKeyValidator.validate_provider(payload.provider)

                logger.info(
                    f"Payload validation successful for update api key {userId}"
                )
            except ValidationException as validation_error:
                logger.warning(
                    f"Api Key payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "apiKeyId": keyId,
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

            api_key = (
                db.query(ApiKey)
                .filter(
                    ApiKey.id == keyId,
                    ApiKey.user_id == userId,
                    ApiKey.is_active == True,
                )
                .first()
            )

            if not api_key:
                logger.warning(
                    f"Api Key update failed: Api Key not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "apiKeyId": keyId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Experience not found or does not belong to this user.",
                )

            updated_fields = {}

            if payload.api_base_url is not None:
                api_key.api_base_url = payload.api_base_url
                updated_fields["api_base_url"] = payload.api_base_url

            if payload.api_version is not None:
                api_key.api_version = payload.api_version
                updated_fields["api_version"] = payload.api_version

            if payload.key_name is not None:
                api_key.key_name = payload.key_name
                updated_fields["key_name"] = payload.key_name

            if payload.key_value is not None:
                api_key.key_value = payload.key_value
                updated_fields["key_value"] = payload.key_value

            if payload.is_active is not None:
                api_key.is_active = payload.is_active
                updated_fields["is_active"] = payload.is_active

            if payload.expires_at is not None:
                api_key.expires_at = payload.expires_at
                updated_fields["expires_at"] = payload.expires_at

            if payload.provider is not None:
                api_key.provider = payload.provider
                updated_fields["provider"] = payload.provider

            if not updated_fields:
                logger.warning(
                    f"No fields provided for update",
                    extra={
                        "userId": userId,
                        "apikeyId": keyId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided for update",
                )

            db.commit()
            db.refresh(api_key)

            return ApiKeyResponse.model_validate(api_key)
        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during api key fetch for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e.orig),
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
                f"Database error during api keys fetch for api key {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching api key.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during fetching api key for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while api key",
            )

    async def delete_api_key(
        self,
        db: Session,
        userId: str,
        keyId: str,
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

            if not keyId:
                logger.error(
                    "Api Key update failed: No api key ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Api Key ID is required",
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

            api_key = (
                db.query(ApiKey)
                .filter(
                    ApiKey.id == keyId,
                    ApiKey.user_id == userId,
                    ApiKey.is_active == True,
                )
                .first()
            )

            if not api_key:
                logger.warning(
                    f"Api Key update failed: Api Key not found or does not belong to user",
                    extra={
                        "userId": userId,
                        "apiKeyId": keyId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Experience not found or does not belong to this user.",
                )

            deleted_api_key_id = api_key.id
            deleted_api_key = api_key.key_name

            logger.info(
                f"Api Key found, proceeding with deletion",
                extra={
                    "userId": userId,
                    "experienceId": deleted_api_key_id,
                },
            )

            db.delete(api_key)
            db.commit()

            logger.info(
                f"Api Key deleted successfully",
                extra={"userId": userId, "apiKeyId": api_key.id},
            )

            return {
                "success": True,
                "message": "Experience deleted successfully",
                "apiKeyId": str(api_key.id),
                "key value": api_key.key_name,
            }

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during api key fetch for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e.orig),
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
                f"Database error during api keys fetch for api key {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching api key.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during fetching api key for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while api key",
            )
