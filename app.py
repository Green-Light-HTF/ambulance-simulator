import asyncio
import json
import threading
import time
import urllib.parse
import urllib.request
from copy import deepcopy

import uvicorn
from fastapi import FastAPI
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.realtime_data_broadcast import RealTimeDataBroadcast

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""
amb_1 = ["23.130966", "72.540977",
         "23.131491", "72.541168",
         "23.132195", "72.541357",
         "23.132495", "72.541478",
         "23.133587", "72.541685",
         "23.134249", "72.541858",
         "23.135288", "72.542131",
         "23.136281", "72.542342",
         "23.136372", "72.542628",
         "23.136246", "72.543248",
         "23.136134", "72.544112",
         "23.136145", "72.544605",
         "23.136024", "72.545518",
         "23.135991", "72.545707",
         "23.135904", "72.545991",
         "23.135839", "72.546440",
         "23.135719", "72.546665",
         "23.135643", "72.547150"]

@app.get("/")
async def get():
    return HTMLResponse(html)


notifier = RealTimeDataBroadcast()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await notifier.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        notifier.remove(websocket)


@app.get("/push/{message}")
async def push_to_connected_websockets(message: str):
    await notifier.push(f"! Push notification: {message} !")


@app.get("/set_patient_loc")
async def get_patient_loc(lat: str, long: str, amb_id: int, init_lat: str, init_long: str):
    try:
        print("here")
        if amb_id == 1:
            track = deepcopy(amb_1)
            while len(track):
                t = track.pop()
                time.sleep(2.5)
                data = {
                    "type": 0,
                    "current_lat": t[0],
                    "current_lng": t[1],
                }
                payload = json.dumps(data)
                await notifier.push(payload)
        # threading.Thread(target=thread_wc, args=(int(amb_id)))
        return True
    except Exception as e:
        raise e


def thread_wc(amb_id: int):
    try:
        if amb_id == 1:
            track = deepcopy(amb_1)
            while len(track):
                t = track.pop()
                time.sleep(2.5)
                data = {
                    "type": 0,
                    "current_lat": t[0],
                    "current_lng": t[1],
                }
                payload = json.dumps(data)
                notifier.push(payload)

    except Exception as e:
        raise e


@app.on_event("startup")
async def startup():
    # Prime the push notification generator
    await notifier.generator.asend(None)


if __name__ == "__main__":
    uvicorn.run(app)