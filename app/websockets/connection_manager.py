from fastapi import logger
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()

        if user_id in self._connections:
            await self.disconnect(user_id)

        self._connections[user_id] = websocket
        logger.info(f"[WS] Connected user={user_id} | active={len(self._connections)}")

    async def disconnect(self, user_id: str):
        ws = self._connections.pop(user_id, None)
        if ws:
            try:
                await ws.close()
            except Exception:
                pass
        logger.info(
            f"[WS] Disconnected user={user_id} | active={len(self._connections)}"
        )

    async def send(self, user_id: str, payload: dict):
        ws = self._connections.get(user_id)
        if not ws:
            logger.debug(f"[WS] No socket for user={user_id} — event dropped")
            return
        try:
            await ws.send_json(payload)
            logger.debug(f"[WS] Sent to user={user_id}: {payload}")
        except Exception as e:
            logger.warning(f"[WS] Send failed user={user_id}: {e}")
            await self.disconnect(user_id)

    def is_connected(self, user_id: str) -> bool:
        return user_id in self._connections


manager = ConnectionManager()
