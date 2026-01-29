import asyncio
import websockets
import json

async def handle_message(websocket, message):
    print("Received message from client:", message)
    try:
        data = json.loads(message)
        if 'offer' in data:
            # Handle the offer message
            offer = data['offer']
            # Here you can generate an answer
            answer = {'type': 'answer', 'sdp': 'Your answer SDP here'}
            await websocket.send(json.dumps(answer))
    except json.JSONDecodeError:
        print("Invalid JSON format")

async def echo(websocket, path):
    print("A client just connected")
    try:
        async for message in websocket:
            await handle_message(websocket, message)
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")

start_server = websockets.serve(echo, "172.25.4.156", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
