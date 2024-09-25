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
        self.active_connections:dict[str, WebSocket]={}
        
    async def connect(self, ws:WebSocket, client_id:str):
        await ws.accept()
        self.active_connections[client_id]=ws
    
    def disconnect(self, client_id:str):
        self.active_connections[client_id]
    
    async def send_personal_message(self, message:str, ws:WebSocket):
        await ws.send_text(message)
        
    async def broadcast(self, message:str, exclude_client_id:str = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude_client_id:
                await connection.send_text(message)

conn_manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_room(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.websocket("/chat")
async def websocket_endpoint(ws:WebSocket):
    client_id = str(uuid.uuid4())
    await conn_manager.connect(ws, client_id)
    
    await conn_manager.send_personal_message(f"Welcome! Your user ID is {client_id}", ws)
    
    await conn_manager.broadcast(f"User {client_id} has joined the chat", exclude_user_id=client_id)
    
    try:
        while True:
            data = await ws.receive_text()
            await conn_manager.send_personal_message(f"You: {data}", ws)
            await conn_manager.broadcast(f"Client {client_id}: {data}",exclude_client_id=client_id)
    except WebSocketDisconnect:
        conn_manager.disconnect(ws)
        await conn_manager.broadcast(f"Client #{client_id} left the chat")