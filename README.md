
# Ambulance - Simulator

Ambulance simulator is a software base replica of an ambulance which broadcast geo-location over web-socket.

## Installation

Install the dependencies and start the server.

### Create Conda Environment for python 3.9
```sh
# activate conda environment
conda activate <env>
# go to project file
cd ambulance-simulator
```

### Install Requirements
```sh
pip install -r requirements.txt
```
By default, the service will run on port 8000

### About FastAPI WebSocket
Checkout https://github.com/authorizon/fastapi_websocket_pubsub