from fastapi import FastAPI, WebSocket, Body
import base64
import cv2
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Dictionary to store frame streams
frame_streams = {}

# Dictionary to store websocket connections for each stream ID
websocket_connections = {}


@app.websocket("/ws/{stream_id}")
async def websocket_endpoint(websocket: WebSocket, stream_id: str):
    await websocket.accept()
    if stream_id not in websocket_connections:
        websocket_connections[stream_id] = []
    websocket_connections[stream_id].append(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Remove the websocket connection when it's closed
        if websocket in websocket_connections[stream_id]:
            websocket_connections[stream_id].remove(websocket)


@app.websocket("/stream/{stream_id}")
async def stream_endpoint(websocket: WebSocket, stream_id: str):
    await websocket.accept()
    try:
        while True:
            # Receive a WebSocket message
            websocket_data = await websocket.receive()
            # print(websocket_data)
            # Check the type of the received message
            # if "bytes" in websocket_data:
            #     # Extract the bytes from the received WebSocket message
            frame_data = websocket_data["bytes"]
            # else:
            #     # If the message is not bytes, log the error and potentially handle other message types
            #     print(f"Expected bytes, received: {websocket_data}")
            #     continue  # Skip processing and wait for the next message

            # Convert frame data to NumPy array
            # frame_np = np.frombuffer(frame_data, dtype=np.uint8)

            # Decode the frame
            # frame = cv2.imdecode(frame_np, flags=cv2.IMREAD_COLOR)

            # Process the frame if needed
            # ... (frame processing code)

            # Send the processed frame back to the clients connected to the same stream ID
            if stream_id in websocket_connections:
                send_coroutines = [
                    ws.send_bytes(frame_data) for ws in websocket_connections[stream_id]
                ]
                await asyncio.gather(*send_coroutines)
                print("Sent frame to clients")

    except Exception as e:
        print(f"An error occurred in streaming: {e}")

    finally:
        # Handle disconnection
        if (
            stream_id in websocket_connections
            and websocket in websocket_connections[stream_id]
        ):
            websocket_connections[stream_id].remove(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80)
