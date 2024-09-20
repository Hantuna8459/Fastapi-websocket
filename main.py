from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    Request,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
import uuid
import json

templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class ConnectionManager():
    def __init__(self)->None:
        self.active_connections:list[WebSocket]=[]
        
    async def connect(self, ws:WebSocket):
        await ws.accept()
        self.active_connections.append(ws)

    def disconnect(self, ws:WebSocket):
        self.active_connections.remove(ws)
        
    # def find_connection_id(self, websocket:WebSocket):
    #     websocket_list = list(self.active_connections.values())
    #     id_list = list(self.active_connections.keys())
        
    #     pos = websocket_list.index(websocket) # find the possition of the Websocket in the list
    #     return id_list[pos]
    
    async def broadcast(self, message:str):
        for connection in self.active_connections:
            await connection.send_text(message)

conn_manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_room(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/chat/{client_id}")
async def websocket_endpoint(ws:WebSocket, client_id: int):
    await conn_manager.connect(ws)
    
    try:
        while True:
            data = await ws.receive_text()
            await conn_manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        conn_manager.disconnect(ws)
        await conn_manager.broadcast(f"Client #{client_id} left the chat")