from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.core.sessions import session_manager
from backend.core.websocket_manager import (
    websocket_manager,
)


router = APIRouter(
    tags=["WebSocket"],
)


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
) -> None:
    """Handle a Telefarm real-time WebSocket connection."""

    if not session_manager.exists(session_id):
        await websocket.close(
            code=1008,
            reason="Invalid or expired session.",
        )
        return

    await websocket_manager.connect(
        session_id,
        websocket,
    )

    try:
        while True:
            message = await websocket.receive_json()

            message_type = message.get(
                "type"
            )

            if message_type == "ping":
                await websocket.send_json(
                    {
                        "type": "pong",
                    }
                )

            elif message_type == "session_status":
                await websocket.send_json(
                    {
                        "type": "session_status",
                        "authenticated": (
                            session_manager.exists(
                                session_id
                            )
                        ),
                    }
                )

    except WebSocketDisconnect:
        websocket_manager.disconnect(
            session_id,
            websocket,
        )

    except Exception:
        websocket_manager.disconnect(
            session_id,
            websocket,
        )
