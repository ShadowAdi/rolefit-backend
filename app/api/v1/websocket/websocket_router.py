"""
app/websockets/ws_router.py
────────────────────────────
WebSocket endpoint: ws://your-api/ws/{user_id}?token=<jwt>

Frontend connects once after login and stays connected.
All generation events arrive here — no polling needed.

Auth: JWT token passed as query param (WebSocket can't send headers).
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.websockets.connection_manager import manager
from app.core.logger import logger
from app.utils.utils import decode_token
import asyncio

router = APIRouter(tags=["WebSocket"])


async def receive_client_messages(websocket: WebSocket, user_id: str):
    """Listen for incoming messages from client"""
    try:
        while True:
            data = await websocket.receive_json()
            logger.debug(f"[WS] Received from client user={user_id}: {data}")
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected user={user_id}")
        raise
    except Exception as e:
        logger.warning(f"[WS] Error receiving message from user={user_id}: {e}")
        raise


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    user_id: str,
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
):
    """
    WebSocket connection for real-time generation events.

    Connect: ws://api/ws/{user_id}?token=<jwt>

    Every event has the shape:
      { type, doc_id, status, message, error? }
    where status ∈ { "pending", "processing", "completed", "failed" }.

    Content generation (resume / cover letter text):
      { type: "generate_resume_content",            status: "completed" }
      { type: "generate_resume_content_failed",     status: "failed", error }
      { type: "cover_letter_generation_completed",  status: "completed" }
      { type: "cover_letter_failed",                status: "failed", error }

    PDF generation (resume):
      { type: "resume_pdf_processing",  status: "processing" }
      { type: "resume_pdf_generated",   status: "completed" }
      { type: "resume_pdf_error",       status: "failed", error }

    PDF generation (cover letter):
      { type: "cover_letter_pdf_processing",  status: "processing" }
      { type: "cover_letter_pdf_generated",   status: "completed" }
      { type: "cover_letter_pdf_error",       status: "failed", error }

    Connection / keepalive:
      { type: "connected", user_id, message }
      { type: "ping" }  ← keepalive from server
    """
    try:
        payload = decode_token(token)
        if not payload:
            await websocket.accept()
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.warning(f"[WS] Auth missing or invalid token for user={user_id}")
            return

        token_user_id = str(payload.get("sub"))
        if token_user_id != user_id:
            await websocket.accept()
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.warning(f"[WS] Auth mismatch: token={token_user_id} path={user_id}")
            return
    except Exception as e:
        logger.warning(f"[WS] Invalid token for user={user_id}: {e}")
        try:
            await websocket.accept()
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        except:
            pass
        return

    logger.info(f"[WS] Token validated for user={user_id}, connecting...")
    await manager.connect(user_id, websocket)
    logger.info(f"[WS] User {user_id} connected successfully")

    # Send welcome message
    try:
        await websocket.send_json(
            {
                "type": "connected",
                "user_id": user_id,
                "message": "Connected to WebSocket server",
            }
        )
        logger.info(f"[WS] Sent welcome message to user={user_id}")
    except Exception as e:
        logger.error(f"[WS] Failed to send welcome message to user={user_id}: {e}")

    try:
        # Listen for incoming client messages
        await receive_client_messages(websocket, user_id)
    except WebSocketDisconnect:
        logger.info(f"[WS] WebSocket disconnected for user={user_id}")
    except Exception as e:
        logger.error(f"[WS] Unexpected error for user={user_id}: {e}", exc_info=True)
    finally:
        await manager.disconnect(user_id)
        logger.info(f"[WS] Cleaned up connection for user={user_id}")
