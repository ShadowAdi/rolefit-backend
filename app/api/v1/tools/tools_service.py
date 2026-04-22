from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from app.models.User import User
from app.models.Tool import Tool
from app.models.UserTool import UserTool
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
from app.core.logger import logger
from app.validators.tool_validators import ToolValidator


class ToolServiceClass:
    def create_tool(
        self, db: Session, payload: ToolCreateRequest, userId
    ) -> ToolCreateResponse:
        """
        Create a new tool in the system for an authenticated user.

        Steps:
        1. Verify user authentication (userId exists)
        2. Validate the request payload
        3. Verify user exists in database
        4. Check if tool name already exists (unique constraint)
        5. Create and save the tool record with current user as creator

        Args:
            db: Database session
            payload: ToolCreateRequest with tool details
            userId: Authenticated user's ID (creator)

        Returns:
            ToolCreateResponse with created tool details

        Raises:
            HTTPException: For various validation, authentication, or database errors
        """
        try:
            logger.info(f"Starting tool creation process for user: {userId}")

            if not userId:
                logger.error(
                    "Tool creation failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            try:
                logger.info(f"Validating tool creation payload for user {userId}")
                validated_name = ToolValidator.validate_name(payload.name)
                validated_name = ToolValidator.validate_name_format(validated_name)
                logger.info(f"Payload validation successful for user {userId}")
            except ValueError as validation_error:
                logger.warning(
                    f"Tool payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "error": str(validation_error),
                        "toolName": payload.name,
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
                    f"Tool creation failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Checking if tool name already exists: {validated_name}")
            # Check for exact match (tools stored in lowercase)
            existing_tool = db.query(Tool).filter(Tool.name == validated_name).first()

            if existing_tool:
                logger.warning(
                    f"Tool creation failed: Tool name already exists",
                    extra={
                        "userId": userId,
                        "toolName": validated_name,
                        "existingToolId": existing_tool.id,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Tool '{validated_name}' already exists. Tool names must be unique.",
                )

            logger.info(
                f"Creating tool record for user {userId} with name: {validated_name}"
            )

            tool = Tool(
                name=validated_name,
                created_by=userId,
            )

            db.add(tool)
            db.commit()
            db.refresh(tool)

            logger.info(
                f"Tool record created successfully",
                extra={
                    "userId": userId,
                    "toolId": tool.id,
                    "toolName": tool.name,
                },
            )

            return ToolCreateResponse.model_validate(tool)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during tool creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e.orig),
                    "toolName": payload.name if payload else None,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tool name already exists. Tool names must be unique.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during tool creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while creating tool.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during tool creation for user {userId}",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the tool.",
            )

    def list_tools(self, db: Session, userId: str = None) -> list[ToolListResponse]:
        """
        Retrieve all tools in the system or user's tools.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Fetch all tools or user's tools based on parameters
        4. Return tools as response objects

        Args:
            db: Database session
            userId: Optional authenticated user's ID (if provided, returns user's tools)

        Returns:
            List of ToolListResponse objects with tool details

        Raises:
            HTTPException: For authentication or database errors
        """
        try:
            if userId:
                logger.info(f"Starting user tool retrieval process for user: {userId}")

                if not userId:
                    logger.error(
                        "Tool retrieval failed: No user ID provided (authentication missing)"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required: User ID is missing",
                    )

                logger.info(f"Verifying user exists with ID: {userId}")
                user = db.query(User).filter(User.id == userId).first()

                if not user:
                    logger.warning(
                        f"Tool retrieval failed: User not found",
                        extra={"userId": userId},
                    )
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User does not exist. Invalid user ID.",
                    )

                logger.info(f"User verified successfully: {userId}")

                logger.info(f"Fetching user's tools for user: {userId}")

                user_tools = (
                    db.query(Tool)
                    .join(UserTool, Tool.id == UserTool.toolId)
                    .filter(UserTool.userId == userId)
                    .all()
                )

                logger.info(
                    f"Successfully retrieved user tools",
                    extra={
                        "userId": userId,
                        "toolCount": len(user_tools),
                    },
                )

                return [ToolListResponse.model_validate(tool) for tool in user_tools]
            else:
                logger.info(f"Fetching all available tools")

                tools = db.query(Tool).all()

                logger.info(
                    f"Successfully retrieved all tools",
                    extra={
                        "toolCount": len(tools),
                    },
                )

                return [ToolListResponse.model_validate(tool) for tool in tools]

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            logger.error(
                f"Database error during tool retrieval",
                extra={
                    "userId": userId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving tools.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during tool retrieval",
                extra={
                    "userId": userId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving tools.",
            )

    def get_tool(self, db: Session, toolId: str) -> ToolGetResponse:
        """
        Retrieve a specific tool by ID.

        Steps:
        1. Verify tool ID is provided
        2. Fetch the specific tool by toolId
        3. Verify tool exists
        4. Return tool as response object

        Args:
            db: Database session
            toolId: Tool ID to retrieve

        Returns:
            ToolGetResponse object with tool details

        Raises:
            HTTPException: For validation or database errors
        """
        try:
            logger.info(
                f"Starting tool retrieval process",
                extra={"toolId": toolId},
            )

            if not toolId:
                logger.error(
                    "Tool retrieval failed: No tool ID provided",
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tool ID is required",
                )

            logger.info(
                f"Fetching tool from database",
                extra={
                    "toolId": toolId,
                },
            )

            tool = db.query(Tool).filter(Tool.id == toolId).first()

            if not tool:
                logger.warning(
                    f"Tool retrieval failed: Tool not found",
                    extra={
                        "toolId": toolId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tool not found.",
                )

            logger.info(
                f"Successfully retrieved tool",
                extra={
                    "toolId": tool.id,
                    "toolName": tool.name,
                },
            )

            return ToolGetResponse.model_validate(tool)

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            logger.error(
                f"Database error during tool retrieval",
                extra={
                    "toolId": toolId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while retrieving tool.",
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during tool retrieval",
                extra={
                    "toolId": toolId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving tool.",
            )

    def update_tool(
        self,
        db: Session,
        toolId: str,
        payload: ToolUpdateRequest,
        userId: str,
    ) -> ToolUpdateResponse:
        """
        Update an existing tool (only creator can update).

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Verify tool exists
        4. Verify user is the creator of the tool
        5. Validate the request payload
        6. Update the tool fields
        7. Save changes and return updated tool

        Args:
            db: Database session
            toolId: Tool ID to update
            payload: ToolUpdateRequest with fields to update
            userId: Authenticated user's ID (must be creator)

        Returns:
            ToolUpdateResponse object with updated tool details

        Raises:
            HTTPException: For authentication, authorization, validation, or database errors
        """
        try:
            logger.info(
                f"Starting tool update process",
                extra={"userId": userId, "toolId": toolId},
            )

            if not userId:
                logger.error(
                    "Tool update failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not toolId:
                logger.error(
                    "Tool update failed: No tool ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tool ID is required",
                )

            try:
                logger.info(f"Validating tool update payload for user {userId}")
                validated_name = ToolValidator.validate_name(payload.name)
                validated_name = ToolValidator.validate_name_format(validated_name)
                logger.info(f"Payload validation successful for user {userId}")
            except ValueError as validation_error:
                logger.warning(
                    f"Tool payload validation failed for user {userId}",
                    extra={
                        "userId": userId,
                        "toolId": toolId,
                        "error": str(validation_error),
                        "toolName": payload.name,
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
                    f"Tool update failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(
                f"Fetching tool from database",
                extra={
                    "userId": userId,
                    "toolId": toolId,
                },
            )

            tool = db.query(Tool).filter(Tool.id == toolId).first()

            if not tool:
                logger.warning(
                    f"Tool update failed: Tool not found",
                    extra={
                        "userId": userId,
                        "toolId": toolId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tool not found.",
                )

            logger.info(f"Tool found, verifying authorization for user {userId}")

            if str(tool.created_by) != str(userId):
                logger.warning(
                    f"Tool update failed: User is not the creator",
                    extra={
                        "userId": userId,
                        "toolId": toolId,
                        "toolCreator": tool.created_by,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the tool creator can update this tool.",
                )

            logger.info(f"Authorization verified, proceeding with update for {toolId}")

            logger.info(f"Checking if new tool name already exists: {validated_name}")
            existing_tool = (
                db.query(Tool)
                .filter(
                    Tool.name == validated_name,
                    Tool.id != toolId,
                )
                .first()
            )

            if existing_tool:
                logger.warning(
                    f"Tool update failed: Tool name already exists",
                    extra={
                        "userId": userId,
                        "toolId": toolId,
                        "newToolName": validated_name,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Tool '{validated_name}' already exists. Tool names must be unique.",
                )

            logger.info(f"Updating tool fields for {toolId}")
            updated_fields = {}

            if payload.name is not None:
                tool.name = validated_name
                updated_fields["name"] = validated_name

            if not updated_fields:
                logger.warning(
                    f"No fields provided for update",
                    extra={
                        "userId": userId,
                        "toolId": toolId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided for update",
                )

            logger.info(
                f"Saving tool updates to database",
                extra={
                    "userId": userId,
                    "toolId": toolId,
                    "updatedFields": list(updated_fields.keys()),
                },
            )

            db.commit()
            db.refresh(tool)

            logger.info(
                f"Tool updated successfully",
                extra={
                    "userId": userId,
                    "toolId": tool.id,
                    "toolName": tool.name,
                    "updatedFields": list(updated_fields.keys()),
                },
            )

            return ToolUpdateResponse.model_validate(tool)

        except HTTPException:
            raise

        except IntegrityError as e:
            db.rollback()
            logger.error(
                f"Database integrity error during tool update for user {userId}",
                extra={
                    "userId": userId,
                    "toolId": toolId,
                    "error": str(e.orig),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tool name already exists. Tool names must be unique.",
            )

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during tool update for user {userId}",
                extra={
                    "userId": userId,
                    "toolId": toolId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while updating tool.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during tool update for user {userId}",
                extra={
                    "userId": userId,
                    "toolId": toolId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating tool.",
            )

    def delete_tool(self, db: Session, toolId: str, userId: str) -> dict:
        """
        Delete a specific tool (only creator can delete).

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Fetch the specific tool by toolId
        4. Verify tool exists
        5. Verify user is the creator of the tool
        6. Delete the tool from database
        7. Return success response with deleted tool details

        Args:
            db: Database session
            toolId: Tool ID to delete
            userId: Authenticated user's ID (must be creator)

        Returns:
            dict with success message and deleted tool ID

        Raises:
            HTTPException: For authentication, authorization, or database errors
        """
        try:
            logger.info(
                f"Starting tool deletion process",
                extra={"userId": userId, "toolId": toolId},
            )

            if not userId:
                logger.error(
                    "Tool deletion failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            if not toolId:
                logger.error(
                    "Tool deletion failed: No tool ID provided",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tool ID is required",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Tool deletion failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(
                f"Fetching tool from database for deletion",
                extra={
                    "userId": userId,
                    "toolId": toolId,
                },
            )

            tool = db.query(Tool).filter(Tool.id == toolId).first()

            if not tool:
                logger.warning(
                    f"Tool deletion failed: Tool not found",
                    extra={
                        "userId": userId,
                        "toolId": toolId,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tool not found.",
                )

            logger.info(f"Tool found, verifying authorization for user {userId}")

            if str(tool.created_by) != str(userId):
                logger.warning(
                    f"Tool deletion failed: User is not the creator",
                    extra={
                        "userId": userId,
                        "toolId": toolId,
                        "toolCreator": tool.created_by,
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the tool creator can delete this tool.",
                )

            deleted_tool_id = tool.id
            deleted_tool_name = tool.name

            logger.info(
                f"Tool found, proceeding with deletion",
                extra={
                    "userId": userId,
                    "toolId": deleted_tool_id,
                    "toolName": deleted_tool_name,
                },
            )

            logger.info(
                f"Deleting tool from database",
                extra={
                    "userId": userId,
                    "toolId": deleted_tool_id,
                },
            )

            db.delete(tool)
            db.commit()

            logger.info(
                f"Tool deleted successfully",
                extra={
                    "userId": userId,
                    "toolId": deleted_tool_id,
                    "toolName": deleted_tool_name,
                },
            )

            return {
                "success": True,
                "message": "Tool deleted successfully",
                "deletedToolId": str(deleted_tool_id),
                "toolName": deleted_tool_name,
            }

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during tool deletion for user {userId}",
                extra={
                    "userId": userId,
                    "toolId": toolId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while deleting tool.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during tool deletion for user {userId}",
                extra={
                    "userId": userId,
                    "toolId": toolId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting tool.",
            )

    def add_tool_to_user(
        self, db: Session, userId: str, payload: AddToolToUserRequest
    ) -> dict:
        """
        Add a tool to a user's profile.

        Handles two scenarios in a single API call:
        1. User selects existing tool: Send toolId -> add directly
        2. User types new tool name: Send toolName -> create if doesn't exist, then add

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Determine tool:
           - If toolId provided: fetch existing tool
           - If toolName provided: find or create tool
        4. Verify tool exists/was created
        5. Check if user already has this tool
        6. Create UserTool record linking user and tool
        7. Return success response

        Args:
            db: Database session
            userId: Authenticated user's ID
            payload: AddToolToUserRequest with either toolId or toolName

        Returns:
            dict with success message and tool details

        Raises:
            HTTPException: For validation, authentication, or database errors
        """
        try:
            logger.info(
                f"Starting tool addition process",
                extra={
                    "userId": userId,
                    "toolId": payload.toolId,
                    "toolName": payload.toolName,
                },
            )

            if not userId:
                logger.error(
                    "Tool addition failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            # Validate that either toolId or toolName is provided
            if not payload.toolId and not payload.toolName:
                logger.error(
                    "Tool addition failed: Neither toolId nor toolName provided"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Either toolId or toolName must be provided",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Tool addition failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            # Handle toolId case - tool already exists
            if payload.toolId:
                logger.info(f"Fetching existing tool by ID: {payload.toolId}")
                tool = db.query(Tool).filter(Tool.id == payload.toolId).first()

                if not tool:
                    logger.warning(
                        f"Tool addition failed: Tool not found",
                        extra={"userId": userId, "toolId": payload.toolId},
                    )
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Tool not found.",
                    )
                logger.info(f"Tool found by ID: {payload.toolId}")

            # Handle toolName case - create if doesn't exist
            else:
                logger.info(f"Processing tool by name: {payload.toolName}")

                try:
                    # Validate and format the tool name
                    validated_name = ToolValidator.validate_name(payload.toolName)
                    validated_name = ToolValidator.validate_name_format(validated_name)
                    logger.info(f"Tool name validated and formatted: {validated_name}")
                except ValueError as validation_error:
                    logger.warning(
                        f"Tool name validation failed",
                        extra={
                            "userId": userId,
                            "error": str(validation_error),
                            "toolName": payload.toolName,
                        },
                    )
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Validation error: {str(validation_error)}",
                    )

                # Check if tool already exists
                logger.info(f"Checking if tool exists: {validated_name}")
                tool = db.query(Tool).filter(Tool.name == validated_name).first()

                if tool:
                    logger.info(
                        f"Tool already exists in database",
                        extra={"toolName": validated_name, "toolId": tool.id},
                    )
                else:
                    # Create new tool
                    logger.info(f"Creating new tool: {validated_name}")
                    tool = Tool(
                        name=validated_name,
                        created_by=userId,
                    )
                    db.add(tool)
                    db.commit()
                    db.refresh(tool)
                    logger.info(
                        f"Tool created successfully",
                        extra={"toolId": tool.id, "toolName": tool.name},
                    )

            # Check if user already has this tool
            logger.info(f"Checking if user already has this tool")
            existing_user_tool = (
                db.query(UserTool)
                .filter(
                    UserTool.userId == userId,
                    UserTool.toolId == tool.id,
                )
                .first()
            )

            if existing_user_tool:
                logger.warning(
                    f"Tool addition failed: User already has this tool",
                    extra={"userId": userId, "toolId": tool.id},
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already has this tool.",
                )

            # Add tool to user
            logger.info(f"Adding tool to user")
            user_tool = UserTool(userId=userId, toolId=tool.id)

            db.add(user_tool)
            db.commit()
            db.refresh(user_tool)

            logger.info(
                f"Tool added to user successfully",
                extra={
                    "userId": userId,
                    "toolId": tool.id,
                    "toolName": tool.name,
                },
            )

            return {
                "success": True,
                "message": "Tool added to user profile successfully",
                "toolId": str(tool.id),
                "toolName": tool.name,
                "toolCreated": False if payload.toolId else True,
            }

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during tool addition for user {userId}",
                extra={
                    "userId": userId,
                    "toolId": payload.toolId,
                    "toolName": payload.toolName,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while adding tool to user.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during tool addition for user {userId}",
                extra={
                    "userId": userId,
                    "toolId": payload.toolId,
                    "toolName": payload.toolName,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while adding tool to user.",
            )

    def remove_tool_from_user(self, db: Session, userId: str, toolId: str) -> dict:
        """
        Remove a tool from a user's profile.

        Steps:
        1. Verify user authentication (userId exists)
        2. Verify user exists in database
        3. Fetch the UserTool record
        4. Verify record exists
        5. Delete the UserTool record

        Args:
            db: Database session
            userId: Authenticated user's ID
            toolId: Tool ID to remove

        Returns:
            dict with success message

        Raises:
            HTTPException: For authentication or database errors
        """
        try:
            logger.info(
                f"Starting tool removal process",
                extra={"userId": userId, "toolId": toolId},
            )

            if not userId:
                logger.error(
                    "Tool removal failed: No user ID provided (authentication missing)"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required: User ID is missing",
                )

            logger.info(f"Verifying user exists with ID: {userId}")
            user = db.query(User).filter(User.id == userId).first()

            if not user:
                logger.warning(
                    f"Tool removal failed: User not found",
                    extra={"userId": userId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not exist. Invalid user ID.",
                )

            logger.info(f"User verified successfully: {userId}")

            logger.info(f"Fetching UserTool record from database")
            user_tool = (
                db.query(UserTool)
                .filter(
                    UserTool.userId == userId,
                    UserTool.toolId == toolId,
                )
                .first()
            )

            if not user_tool:
                logger.warning(
                    f"Tool removal failed: User does not have this tool",
                    extra={"userId": userId, "toolId": toolId},
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User does not have this tool.",
                )

            logger.info(f"Removing tool from user")
            db.delete(user_tool)
            db.commit()

            logger.info(
                f"Tool removed from user successfully",
                extra={
                    "userId": userId,
                    "toolId": toolId,
                },
            )

            return {
                "success": True,
                "message": "Tool removed from user profile successfully",
                "toolId": str(toolId),
            }

        except HTTPException:
            raise

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(
                f"Database error during tool removal for user {userId}",
                extra={
                    "userId": userId,
                    "toolId": toolId,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while removing tool from user.",
            )

        except Exception as e:
            db.rollback()
            logger.error(
                f"Unexpected error during tool removal for user {userId}",
                extra={
                    "userId": userId,
                    "toolId": toolId,
                    "error": str(e),
                    "errorType": type(e).__name__,
                },
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while removing tool from user.",
            )
