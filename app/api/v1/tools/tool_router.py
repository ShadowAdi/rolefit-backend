from fastapi import APIRouter, Depends, status, HTTPException
from app.schema.Tool import (
    ToolCreateRequest,
    ToolUpdateRequest,
    AddToolToUserRequest,
)
from app.response.tool_responses import (
    ToolCreateResponse,
    ToolGetResponse,
    ToolListResponse,
    ToolUpdateResponse,
)
from sqlalchemy.orm import Session
from app.db.db import get_db
from .tools_service import ToolServiceClass
from app.models.User import User
from app.response.base import APIResponse
from app.dependency.dependencies import get_current_user
from app.core.logger import logger
from typing import List

router = APIRouter(prefix="", tags=["Tools"])

ToolService = ToolServiceClass()


@router.post(
    "/",
    response_model=ToolCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tool(
    data: ToolCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new tool in the system for the authenticated user.

    Args:
        data: Tool creation request data (name)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        ToolCreateResponse: Created tool with id, name, created_by, created_at

    Raises:
        HTTPException: If validation fails, user not found, tool already exists, or database error
    """
    try:
        logger.info(
            f"Tool creation request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        tool = ToolService.create_tool(db=db, payload=data, userId=str(current_user.id))

        logger.info(
            f"Tool creation endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "toolId": str(tool.id),
            },
        )

        return APIResponse(
            data=tool, message="Tool Added Successfully", status_code=201, success=True
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in tool creation: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in tool creation endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/",
    response_model=List[ToolListResponse],
    status_code=status.HTTP_200_OK,
)
async def list_tools(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all available tools in the system or user's tools.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        List[ToolListResponse]: List of all available tools

    Raises:
        HTTPException: If database error occurs
    """
    try:
        logger.info(
            f"Tool list retrieval request received for user: {current_user.id}",
            extra={"userId": str(current_user.id)},
        )

        tools = ToolService.list_tools(db=db)

        logger.info(
            f"Tool list retrieval endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "toolCount": len(tools),
            },
        )

        return APIResponse(
            data=tools,
            message="Tool Fetched Successfully",
            status_code=200,
            success=True,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in tool list retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in tool list retrieval endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get(
    "/{toolId}",
    response_model=ToolGetResponse,
    status_code=status.HTTP_200_OK,
)
async def get_tool(
    toolId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific tool by ID.

    Args:
        toolId: Tool ID to retrieve
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        ToolGetResponse: Tool details with all information

    Raises:
        HTTPException: If tool not found or database error
    """
    try:
        logger.info(
            f"Tool retrieval request received for user: {current_user.id}, tool: {toolId}",
            extra={"userId": str(current_user.id), "toolId": toolId},
        )

        tool = ToolService.get_tool(db=db, toolId=toolId)

        logger.info(
            f"Tool retrieval endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "toolId": str(tool.id),
            },
        )

        return APIResponse(
            data=tool,
            message="Tool Fetched Successfully",
            status_code=200,
            success=True,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in tool retrieval: {http_exc.detail}",
            extra={"userId": str(current_user.id), "toolId": toolId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in tool retrieval endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "toolId": toolId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.patch(
    "/{toolId}",
    response_model=ToolUpdateResponse,
    status_code=status.HTTP_200_OK,
)
async def update_tool(
    toolId: str,
    data: ToolUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing tool for the authenticated user (only creator can update).

    Args:
        toolId: Tool ID to update
        data: Tool update request data (name)
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        ToolUpdateResponse: Updated tool data

    Raises:
        HTTPException: If validation fails, tool not found, not authorized, or database error
    """
    try:
        logger.info(
            f"Tool update request received for user: {current_user.id}, tool: {toolId}",
            extra={"userId": str(current_user.id), "toolId": toolId},
        )

        tool = ToolService.update_tool(
            db=db,
            toolId=toolId,
            payload=data,
            userId=str(current_user.id),
        )

        logger.info(
            f"Tool update endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "toolId": str(tool.id),
            },
        )

        return APIResponse(
            data=tool,
            message="Tool Updated Successfully",
            status_code=200,
            success=True,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in tool update: {http_exc.detail}",
            extra={"userId": str(current_user.id), "toolId": toolId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in tool update endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "toolId": toolId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete(
    "/{toolId}",
    status_code=status.HTTP_200_OK,
)
async def delete_tool(
    toolId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a tool (only creator can delete).

    Args:
        toolId: Tool ID to delete
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        dict: Deletion confirmation with message, toolId, and toolName

    Raises:
        HTTPException: If tool not found, not authorized, or database error
    """
    try:
        logger.info(
            f"Tool deletion request received for user: {current_user.id}, tool: {toolId}",
            extra={"userId": str(current_user.id), "toolId": toolId},
        )

        response = ToolService.delete_tool(
            db=db, toolId=toolId, userId=str(current_user.id)
        )

        logger.info(
            f"Tool deletion endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "toolId": toolId},
        )

        return APIResponse(
            data=tool,
            message="Tool Deleted Successfully",
            status_code=200,
            success=True,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in tool deletion: {http_exc.detail}",
            extra={"userId": str(current_user.id), "toolId": toolId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in tool deletion endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "toolId": toolId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.post(
    "/user/add",
    status_code=status.HTTP_200_OK,
)
async def add_tool_to_user(
    data: AddToolToUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a tool to user's profile.

    Handles two scenarios in one API call:
    1. User selects existing tool: Send toolId -> add directly
    2. User types new tool name: Send toolName -> create if doesn't exist, then add

    Args:
        data: AddToolToUserRequest with either toolId or toolName
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        dict: Success message with toolId, toolName, and toolCreated flag

    Raises:
        HTTPException: If validation fails, user not found, or database error
    """
    try:
        logger.info(
            f"Add tool to user request received for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "toolId": data.toolId,
                "toolName": data.toolName,
            },
        )

        response = ToolService.add_tool_to_user(
            db=db, userId=str(current_user.id), payload=data
        )

        logger.info(
            f"Add tool to user endpoint completed successfully for user: {current_user.id}",
            extra={
                "userId": str(current_user.id),
                "toolId": response.get("toolId"),
            },
        )

        return APIResponse(
            data=response,
            message="Tool added Successfully",
            status_code=200,
            success=True,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in add tool to user: {http_exc.detail}",
            extra={"userId": str(current_user.id)},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in add tool to user endpoint: {str(e)}",
            extra={"userId": str(current_user.id), "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.delete(
    "/user/remove/{toolId}",
    status_code=status.HTTP_200_OK,
)
async def remove_tool_from_user(
    toolId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove a tool from user's profile.

    Args:
        toolId: Tool ID to remove
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        dict: Success message with toolId

    Raises:
        HTTPException: If user doesn't have tool or database error
    """
    try:
        logger.info(
            f"Remove tool from user request received for user: {current_user.id}, tool: {toolId}",
            extra={"userId": str(current_user.id), "toolId": toolId},
        )

        response = ToolService.remove_tool_from_user(
            db=db, userId=str(current_user.id), toolId=toolId
        )

        logger.info(
            f"Remove tool from user endpoint completed successfully for user: {current_user.id}",
            extra={"userId": str(current_user.id), "toolId": toolId},
        )

        return APIResponse(
            data=response,
            message="Tool removed Successfully",
            status_code=200,
            success=True,
        )

    except HTTPException as http_exc:
        logger.warning(
            f"HTTP exception in remove tool from user: {http_exc.detail}",
            extra={"userId": str(current_user.id), "toolId": toolId},
        )
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in remove tool from user endpoint: {str(e)}",
            extra={
                "userId": str(current_user.id),
                "toolId": toolId,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
