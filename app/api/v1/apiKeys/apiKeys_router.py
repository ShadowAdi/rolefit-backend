from fastapi import APIRouter, Depends, status, HTTPException
from app.schema.ApiKeys import ApiKeyCreateRequest, ApiKeyResponse, ApiKeyUpdateRequest
from app.schema.ApiKeys import ApiKeyResponse
from sqlalchemy.orm import Session
from app.db.db import get_db
from .apiKeys_service import ApiKeysServiceClass
from app.models.User import User
from app.dependency.dependencies import get_current_user
from app.core.logger import logger
from app.response.base import APIResponse
from typing import List
from app.models.ApiKeys import ApiKey
from app.helpers.api_key_encryption import api_key_encryption

router = APIRouter(prefix="", tags=["api-keys"])

ApiKeysService = ApiKeysServiceClass()


@router.post(
    "/",
    response_model=APIResponse[ApiKeyResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_apiKey(
    data: ApiKeyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:
        logger.info(
            f"Api Keys creation request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        apiKey = await ApiKeysService.create_api_keys(
            db=db, payload=data, userId=str(current_user.id)
        )

        logger.info(
            f"Api Keys creation endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "apiKeyId": str(apiKey.id),
            },
        )

        return APIResponse(
            status_code=201,
            success=True,
            message="Api Key Created Successfully",
            data=apiKey,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in api creation: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in api creation endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/",
    response_model=APIResponse[List[ApiKeyResponse]],
    status_code=status.HTTP_200_OK,
)
async def list_api_keys(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):

    try:

        apiKeys = await ApiKeysService.get_api_keys(db=db, userId=str(current_user.id))

        return APIResponse(
            status_code=200,
            success=True,
            message="Api Keys Fetched Successfully",
            data=apiKeys,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in api keys list retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in api keys list retrieval endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/{achievementId}",
    response_model=APIResponse[ApiKeyResponse],
    status_code=status.HTTP_200_OK,
)
async def get_api_Key(
    apiKeyId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:

        apiKEY = await ApiKeysService.get_api_key(
            db=db, userId=str(current_user.id), keyId=apiKeyId
        )

        return APIResponse(
            status_code=200,
            success=True,
            message="Api Key Fetched Successfully",
            data=apiKEY,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in sapi key retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id), "achievementId": apiKeyId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in api Key retrieval endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.patch(
    "/{apiKeyId}",
    response_model=APIResponse[ApiKeyResponse],
    status_code=status.HTTP_200_OK,
)
async def update_apiKey(
    apiKeyId: str,
    data: ApiKeyUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:

        apiKey = await ApiKeysService.update_api_key(
            db=db,
            payload=data,
            userId=str(current_user.id),
            keyId=apiKeyId,
        )

        return APIResponse(
            status_code=200,
            success=True,
            message="Api Key Updated Successfully",
            data=apiKey,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in api key update: {http_exc.detail}",
            extra={"userId": str(current_user.id), "apiKeyId": apiKeyId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in achievement update endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "apiKeyId": apiKeyId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete(
    "/{apiKeyId}",
    status_code=status.HTTP_200_OK,
)
async def delete_api_key(
    apiKeyId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:

        response = await ApiKeysService.delete_api_key(
            db=db, userId=str(current_user.id), keyId=apiKeyId
        )

        return APIResponse(
            status_code=200,
            success=True,
            message="Achievment Deleted Successfully",
            data=response,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in api key deletion: {http_exc.detail}",
            extra={"userId": str(current_user.id), "achievementId": apiKeyId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in api key deletion endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "achievementId": apiKeyId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


# app/api/v1/apiKeys/apiKeys_router.py
@router.post("/test/{key_id}")
async def test_api_key_endpoint(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Test if an API key is valid"""
    try:
        api_key = (
            db.query(ApiKey)
            .filter(ApiKey.id == key_id, ApiKey.user_id == current_user.id)
            .first()
        )

        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")

        # Decrypt and test the key
        decrypted_key = api_key_encryption.decrypt_api_key(api_key.key_value)

        # Test the key
        is_valid = await ApiKeysServiceClass().test_api_key(
            api_key.provider.value, decrypted_key
        )

        return {
            "success": True,
            "is_valid": is_valid,
            "provider": api_key.provider.value,
        }
    except Exception as e:
        return {"success": False, "is_valid": False, "error": str(e)}
