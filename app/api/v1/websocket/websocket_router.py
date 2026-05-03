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

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    user_id: str,
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
):
    """
    WebSocket connection for real-time generation events.

    Connect: ws://api/ws/{user_id}?token=<jwt>

    Events you'll receive:
      { type: "resume_completed",       doc_id, status, message }
      { type: "resume_failed",          doc_id, status, message, error }
      { type: "cover_letter_completed", doc_id, status, message }
      { type: "cover_letter_failed",    doc_id, status, message, error }
      { type: "pdf_ready",              doc_id, status, message }
      { type: "ping" }  ← keepalive from server
    """
    try:
        payload = decode_token(token)
        token_user_id = str(payload.get("sub"))
        if token_user_id != user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.warning(f"[WS] Auth mismatch: token={token_user_id} path={user_id}")
            return
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning(f"[WS] Invalid token for user={user_id}")
        return

    await manager.connect(user_id, websocket)

    try:
        # Keep connection alive — receive loop
        # Client can send { type: "ping" } to check connection
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected user={user_id}")
    except Exception as e:
        logger.warning(f"[WS] Unexpected disconnect user={user_id}: {e}")
    finally:
        await manager.disconnect(user_id)
