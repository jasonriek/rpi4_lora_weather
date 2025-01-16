from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import serial
import asyncio

# Configure the serial connection to the LoRa module
lora_serial = serial.Serial(
    port='/dev/serial0',  # UART port on Raspberry Pi
    baudrate=115200,
    timeout=1
)

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

connected_clients = set()  # To track WebSocket clients

@app.get("/")
async def get(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming data."""
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def stream_lora_data():
    """Stream LoRa data to WebSocket clients."""
    buffer = ""
    while True:
        try:
            if lora_serial.in_waiting > 0:
                incoming_data = lora_serial.read(lora_serial.in_waiting).decode(errors="ignore")
                buffer += incoming_data

                # Check for complete messages based on newline delimiter
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        print(f"Raw LoRa Data: {line}")
                        # Send data to all connected WebSocket clients
                        for client in connected_clients:
                            await client.send_text(line)
        except Exception as e:
            print(f"Error in receiving LoRa data: {e}")
        await asyncio.sleep(0.1)  # Prevent tight loop

# Run the LoRa data streaming task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(stream_lora_data())
