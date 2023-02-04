import asyncio
import json
import threading
import time
import urllib.parse
import urllib.request
from copy import deepcopy
import requests
import uvicorn
from fastapi import FastAPI
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.realtime_data_broadcast import RealTimeDataBroadcast
import websockets


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
amb_1 = [
    ("23.03572650409564", "72.49419836801214"),
    ("23.03658130138197", "72.49474573600173"),
    ("23.037191867552142", "72.49516040872112"),
    ("23.037710846621387", "72.4953760385352"),
    ("23.038260351692298", "72.49587364579847"),
    ("23.03859615924345", "72.49598975415991"),
    ("23.039038813372947", "72.49630490542664"),
    ("23.039649368406447", "72.49665323051093"),
    ("23.040412558307185", "72.49731670686195"),
    ("23.041099425521193", "72.49759868431114"),
    ("23.04218140580732", "72.49787283573086"),
    ("23.043086509437707", "72.49792747904596"),
    ("23.0438910408924", "72.49811873064887"),
    ("23.04420530968668", "72.49811873064887"),
    ("23.044808703716217", "72.49824167810787"),
    ("23.045776642772434", "72.49837828639484"),
    ("23.047737640605636", "72.49884275457332"),
    ("23.04933407288394", "72.49896570203231"),
    ("23.050038005513773", "72.49911597114887"),
    ("23.050641373410397", "72.49927990109421"),
    ("23.05119445827384", "72.4996077609849"),
    ("23.051936091310075", "72.5000585683535"),
    ("23.05276570977568", "72.50059134067585"),
    ("23.05359532312925", "72.50146563371767"),
    ("23.054198675084525", "72.5022716226156"),
    ("23.054663757037872", "72.5030229681984"),
    ("23.055015709880507", "72.5037196704661"),
    ("23.055380231497494", "72.50452565936402"),
    ("23.05589558802416", "72.50591906393416"),
    ("23.05651149925893", "72.50750372007245"),
    ("23.057177685789316", "72.50910203703951"),
    ("23.057227963884216", "72.50949820107408"),
    ("23.05776845223944", "72.51044079828502"),
    ("23.05822151168113", "72.51178575067055"),
    ("23.05868428489764", "72.51281960581716"),
    ("23.05912134703003", "72.51402111314968"),
    ("23.059352732290257", "72.51555792485411"),
    ("23.059172766011123", "72.51620059156686"),
    ("23.059095637532124", "72.5171226785895")
]

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
async def set_patient_loc(lat: str, long: str, amb_id: int, init_lat: str, init_long: str):
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
                    "amb_id": amb_id,
                    "message": None
                }
                payload = json.dumps(data)
                await notifier.push(payload)

                # url = f"http://localhost:10001/track_live_location?lat={t[0]}&long={t[1]}&user_id=1&amb_id=1"
                # response = requests.get(url).json()
                #
                # if len(response['numbers_to_notify']) > 0:
                #     data = {
                #         "type": 0,
                #         "current_lat": t[0],
                #         "current_lng": t[1],
                #         "amb_id": amb_id,
                #         "message": response['numbers_to_notify']
                #     }
                #     payload = json.dumps(data)
                #     await notifier.push(payload)
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
    uvicorn.run(app, host="0.0.0.0", port=8000)