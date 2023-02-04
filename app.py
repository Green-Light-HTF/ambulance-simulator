import json
import time
from copy import deepcopy
from fastapi.middleware.cors import CORSMiddleware
import requests
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
amb_1 = [
    ("23.058254250939743", "72.51682393703403"),
    ("23.058436876861652", "72.51687422845268"),
    ("23.058605929017958", "72.51691781434901"),
    ("23.05877251305084", "72.51696140024538"),
    ("23.058908865014043", "72.516997610067"),
    ("23.05911808704106", "72.51705052402419"),
    ("23.0592353124157", "72.51707332280064"),
    ("23.05919089018048", "72.51727448847524"),
    ("23.05910636449446", "72.51765200939477"),
    ("23.059023689685", "72.51800740208947"),
    ("23.05893854691919", "72.51840302791923"),
    ("23.058832426874737", "72.51886235621265"),
    ("23.058744199099337", "72.5192284777431"),
    ("23.058668310827713", "72.51959124651137"),
    ("23.058600778933073", "72.51984572143684"),
    ("23.05850082840889", "72.52022592456296"),
    ("23.05837990051441", "72.52019239695066"),
    ("23.058136810441336", "72.52012601227729"),
    ("23.057992436944986", "72.52008309693338"),
    ("23.05784868027138", "72.52004688711106"),
    ("23.05770677439557", "72.5200059834239"),
    ("23.057563017416765", "72.51996776194535"),
    ("23.057420494253826", "72.51992886991492"),
    ("23.057133596520323", "72.51984572143598"),
    ("23.05684608118731", "72.51976994903127"),
    ("23.056559643976016", "72.51968446116213"),
    ("23.0562733613955", "72.51960131268235"),
    ("23.055845046558648", "72.51947608259073"),
    ("23.055703755558202", "72.51943450835128"),
    ("23.05541623717234", "72.51935135987168"),
    ("23.05498622414654", "72.5192290428297"),
    ("23.05469808722832", "72.51914321214142"),
    ("23.054271125185892", "72.51902050107952"),
    ("23.05369841062351", "72.51885427884137"),
    ("23.053419472252397", "72.51877229370183"),
    ("23.05309060975501", "72.51852955378631"),
    ("23.052712386040945", "72.51839477278354"),
    ("23.052192249574954", "72.51823316969075"),
    ("23.051789688480948", "72.51811009319495"),
    ("23.051310965599345", "72.5179408611521"),
    ("23.050562563501302", "72.51766815355256"),
    ("23.04966626428615", "72.51728799960104"),
    ("23.049193626704874", "72.51708616337223"),
    ("23.048647385311956", "72.51684808895553"),
    ("23.047754601827513", "72.51642693665671"),
    ("23.0473014836236", "72.5162015747699"),
    ("23.04649557836107", "72.51581631258523"),
    ("23.04609101392538", "72.51561524857544"),
    ("23.04530335435288", "72.51521945983853"),
    ("23.04386767253031", "72.51451694395264"),
    ("23.04278602665753", "72.51401221263801"),
    ("23.04172134380935", "72.5134821679796"),
    ("23.040657726920333", "72.51294395082768"),
    ("23.039542084053704", "72.5123936724405"),
    ("23.03846450170867", "72.5118670663851"),
    ("23.0376834235571", "72.51147478663809"),
    ("23.03692847192831", "72.51111728750492"),
    ("23.035989190689047", "72.51066384723458"),
    ("23.034783706285562", "72.51006842261859"),
    ("23.033196060928187", "72.5093786596816"),
    ("23.031653178885048", "72.50886029001633"),
    ("23.030475743809887", "72.50863618075998"),
    ("23.027362799886745", "72.50763135434995"),
    ("23.027195585493104", "72.50717031133802"),
    ("23.027354439165432", "72.50720210740766"),
    ("23.028406770312802", "72.50756473747558"),
    ("23.029826777899025", "72.50803357712968"),
    ("23.031241896337967", "72.50850221258123"),
    ("23.031970676815163", "72.50883485712518"),
    ("23.033178022137093", "72.50920531271308"),
    ("23.033593064877195", "72.50920876503999"),
    ("23.034150844910908", "72.50942678207106")
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
            track.reverse()
            time.sleep(7)
            # while True:
            #     if len(notifier.connections) > 0:
            #         break
            while len(track):
                print("iterating")
                t = track.pop()
                time.sleep(1)
                data = {
                    "type": 0,
                    "current_lat": t[0],
                    "current_lng": t[1],
                    "amb_id": amb_id,
                    "message": None
                }
                payload = json.dumps(data)
                await notifier.push(payload)

                try:
                    url = f"http://localhost:10001/track_live_location?lat={t[0]}&long={t[1]}&user_id=1&amb_id=1"
                    response = requests.get(url).json()
                    if isinstance(response, str):
                        response = eval(response)
                    if response:
                        if len(response['numbers_to_notify']) > 0:
                            data = {
                                "type": 0,
                                "current_lat": t[0],
                                "current_lng": t[1],
                                "amb_id": amb_id,
                                "message": response['numbers_to_notify']
                            }
                            payload = json.dumps(data)
                            await notifier.push(payload)
                except Exception as e:
                    pass
            #
            # # Going back to hospital
            # print("Iteration 2 started")
            # track2 = deepcopy(amb_1)
            # # track2.reverse()
            # while len(track2):
            #     print("iterating")
            #     t = track.pop()
            #     time.sleep(2)
            #     data = {
            #         "type": 1,
            #         "current_lat": t[0],
            #         "current_lng": t[1],
            #         "amb_id": amb_id,
            #         "message": None
            #     }
            #     payload = json.dumps(data)
            #     await notifier.push(payload)
            #
            #     try:
            #         url = f"http://localhost:10001/track_live_location?lat={t[0]}&long={t[1]}&user_id=1&amb_id=1"
            #         response = requests.get(url).json()
            #         if isinstance(response, str):
            #             response = eval(response)
            #         if response:
            #             if len(response['numbers_to_notify']) > 0:
            #                 data = {
            #                     "type": 0,
            #                     "current_lat": t[0],
            #                     "current_lng": t[1],
            #                     "amb_id": amb_id,
            #                     "message": response['numbers_to_notify']
            #                 }
            #                 payload = json.dumps(data)
            #                 await notifier.push(payload)
            #     except Exception as e:
            #         pass
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
async def startup():
    # Prime the push notification generator
    await notifier.generator.asend(None)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
