# websocket_client.py
import asyncio
import websockets

async def hello():
    uri = "ws://127.0.0.1:5678"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello server!")
        response = await websocket.recv()
        print(f"Received from server: {response}")

asyncio.get_event_loop().run_until_complete(hello())

