import json
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from starlette.websockets import WebSocketState

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dictionary to store websocket connections for each stream ID
websocket_connections: Dict[str, list[WebSocket]] = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"User {user_id} connected.")

    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            if (
                not websocket.client_state == WebSocketState.DISCONNECTED
            ):  # Check if already disconnected
                await websocket.close()
                print(f"Closed connection for user {user_id}")
            del self.active_connections[user_id]

    async def send_notification(self, user_id: str, notification_type: str, data: dict):
        message = json.dumps({"type": notification_type, **data})
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)
            print(f"Sent {notification_type} notification to user {user_id}.")

    async def broadcast(self, message: str, type: str):
        disconnected_user_ids = []
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_json({"data": message, "type": type})
                print(f"Broadcasted message to user {user_id}.")
            except WebSocketDisconnect:
                disconnected_user_ids.append(user_id)
                print(f"User {user_id} disconnected during broadcast.")
        for user_id in disconnected_user_ids:
            await self.disconnect(user_id)


manager = ConnectionManager()


@app.websocket("/ws/notifications/{user_id}")
async def websocket_notification_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                message_type = message_data.get("type")
                print(f"Received {message_type} message from user {user_id}.")
                if message_type in ["alert", "message", "heartbeat"]:
                    await manager.send_notification(user_id, message_type, message_data)
                else:
                    await manager.send_notification(
                        user_id, "error", {"details": "Unknown message type"}
                    )
            except WebSocketDisconnect:
                print(f"WebSocket disconnected for user {user_id}")
                break

    except WebSocketDisconnect:
        await manager.disconnect(user_id)
        await manager.send_notification(
            user_id,
            "status",
            {"details": "A client disconnected from the notification service."},
        )
        print(f"User {user_id} disconnected with exception.")
    finally:
        await manager.disconnect(user_id)


@app.websocket("/ws/{stream_id}")
async def websocket_stream_endpoint(websocket: WebSocket, stream_id: str):
    await websocket.accept()
    websocket_connections.setdefault(stream_id, []).append(websocket)
    print(f"WebSocket connected for stream {stream_id}.")
    try:
        while True:
            await websocket.receive()
    except WebSocketDisconnect:
        print(f"WebSocket for stream {stream_id} disconnected with exception.")
    finally:
        websocket_connections[stream_id].remove(websocket)
        if not websocket_connections[stream_id]:
            del websocket_connections[stream_id]
            print(f"No more connections for stream {stream_id}.")


@app.websocket("/stream/{stream_id}")
async def stream_endpoint(websocket: WebSocket, stream_id: str):
    await websocket.accept()
    print(f"Stream {stream_id} accepted connection.")
    await manager.broadcast("streamingStarted", "success")
    try:
        while True:
            websocket_data = await websocket.receive()
            if "bytes" in websocket_data:
                frame_data = websocket_data["bytes"]
                if stream_id in websocket_connections:
                    send_coroutines = [
                        ws.send_bytes(frame_data)
                        for ws in websocket_connections[stream_id]
                    ]
                    await asyncio.gather(*send_coroutines)
                    print(f"Streaming data for stream {stream_id}.")
            else:
                print(f"Expected bytes, received: {websocket_data}")
    except WebSocketDisconnect:
        await manager.broadcast("Streaming ended.", "end")
        print(f"Stream {stream_id} disconnected with exception.")
    finally:
        if (
            stream_id in websocket_connections
            and websocket in websocket_connections[stream_id]
        ):
            websocket_connections[stream_id].remove(websocket)
            if not websocket_connections[stream_id]:
                del websocket_connections[stream_id]
                print(f"Stream {stream_id} has no more active connections.")


if __name__ == "__main__":
    import uvicorn

    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=80)
