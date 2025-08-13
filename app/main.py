import os
import sys
import json
import threading
import webbrowser
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends, HTTPException, Header, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from starlette.middleware.sessions import SessionMiddleware

import jwt
import logging

# --- Cargar .env ---
load_dotenv()

# --- Configuración general / secretos ---
SESSION_SECRET = os.getenv("SESSION_SECRET", "cambiar_por_session_secret")
JWT_SECRET = os.getenv("JWT_SECRET", "cambiar_por_jwt_secret")
JWT_ALG = "HS256"
JWT_EXP_DAYS = int(os.getenv("JWT_EXP_DAYS", "30"))

# Credenciales de acceso
USERNAME = os.getenv("IOT_USERNAME", "usuario_iot1")
PASSWORD = os.getenv("IOT_PASSWORD", "contraseña_segura_iot1")

# --- MQTT ---
from app.mqtt_handler import start_mqtt, publish, register_message_callback, TOPICS

DATA_FILE = "datos.json"
HISTORY_FILE = "historial.json"
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "100"))

# --- App ---
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# Función para encontrar recursos
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Montar estáticos y templates
app.mount("/static", StaticFiles(directory=resource_path("static")), name="static")
templates = Jinja2Templates(directory=resource_path("templates"))

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("iot-dashboard")

# --- Modelos ---
class ModoRequest(BaseModel):
    modo: int

class ServoRequest(BaseModel):
    angulo: int

# --- JWT helpers ---
def create_token():
    payload = {"exp": datetime.utcnow() + timedelta(days=JWT_EXP_DAYS)}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def verify_token(authorization: str = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Token inválido o ausente")
    token = authorization[7:]
    try:
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return True
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token inválido")

# --- Manejo de datos ---
def write_json_atomic(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

def append_to_history(new_entry):
    try:
        if os.path.exists(resource_path(HISTORY_FILE)):
            with open(resource_path(HISTORY_FILE), "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = []

        history.append(new_entry)
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]

        write_json_atomic(resource_path(HISTORY_FILE), history)
    except Exception as e:
        logger.warning("⚠️ Error guardando historial: %s", e)

def update_data_and_history(key, value):
    try:
        if os.path.exists(resource_path(DATA_FILE)):
            with open(resource_path(DATA_FILE), "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}
    except Exception:
        data = {}

    data[key] = value
    write_json_atomic(resource_path(DATA_FILE), data)

    required_keys = ["temperature", "humidity", "lumen", "servo_value", "door_state"]
    if all(k in data for k in required_keys):
        hist_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": data.get("temperature"),
            "humidity": data.get("humidity"),
            "lumen": data.get("lumen"),
            "servo_value": data.get("servo_value"),
            "door_state": data.get("door_state")
        }
        append_to_history(hist_entry)

# --- Callback MQTT ---
def handle_mqtt_message(topic, message):
    print(f"[MQTT] {topic} => {message}")

register_message_callback(handle_mqtt_message)

@app.on_event("startup")
async def startup_event():
    print("Iniciando servidor FastAPI...")
    start_mqtt()

# --- Login / sesión ---
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("authenticated"):
        return RedirectResponse(url="/panel", status_code=302)
    return """
    <html>
      <head><meta charset="utf-8"><title>Login</title></head>
      <body>
        <h2>Login</h2>
        <form method="post" action="/login">
          Usuario: <input type="text" name="username"><br>
          Contraseña: <input type="password" name="password"><br>
          <input type="submit" value="Ingresar">
        </form>
      </body>
    </html>
    """

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == USERNAME and password == PASSWORD:
        request.session["authenticated"] = True
        return RedirectResponse(url="/panel", status_code=302)
    return RedirectResponse(url="/", status_code=302)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

# --- Panel protegido ---
@app.get("/panel", response_class=HTMLResponse)
def serve_panel(request: Request):
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/", status_code=302)

    try:
        with open(resource_path(DATA_FILE), "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {
            "temperature": "--",
            "humidity": "--",
            "lumen": "--",
            "servo_value": "--",
            "door_state": False,
            "mode": 1
        }
    return templates.TemplateResponse("dashboard.html", {"request": request, "data": data})

# --- Token JWT ---
@app.get("/get_token")
def get_token(request: Request):
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=403, detail="Acceso no autorizado")
    token = create_token()
    return {"token": token}

# --- API protegida ---
@app.get("/status")
def status(user: bool = Depends(verify_token)):
    if not os.path.exists(resource_path(DATA_FILE)):
        return {"error": "No hay datos aún"}
    with open(resource_path(DATA_FILE), "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/historial")
def get_historial(user: bool = Depends(verify_token)):
    if not os.path.exists(resource_path(HISTORY_FILE)):
        return []
    with open(resource_path(HISTORY_FILE), "r", encoding="utf-8") as f:
        return json.load(f)

@app.post("/modo")
def cambiar_modo(req: ModoRequest, user: bool = Depends(verify_token)):
    logger.info("Cambio de modo a: %s", req.modo)
    try:
        if os.path.exists(resource_path(DATA_FILE)):
            with open(resource_path(DATA_FILE), "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}
    except Exception:
        data = {}

    data["mode"] = req.modo
    write_json_atomic(resource_path(DATA_FILE), data)

    try:
        publish("mode", req.modo)
    except Exception as e:
        logger.warning("No se pudo publicar modo por MQTT: %s", e)

    return {"ok": True, "modo": req.modo}

@app.post("/servo")
def cambiar_servo(req: ServoRequest, user: bool = Depends(verify_token)):
    logger.info("Movimiento manual del servo: %s°", req.angulo)
    ang = max(0, min(180, int(req.angulo)))
    try:
        publish("servo_value", ang)
    except Exception as e:
        logger.warning("No se pudo publicar servo por MQTT: %s", e)
        return {"ok": False, "error": str(e)}
    update_data_and_history("servo_value", ang)
    return {"ok": True, "servo": ang}

# --- Servicios background ---
def start_background_services():
    try:
        start_mqtt()
        logger.info("Servicio MQTT iniciado.")
    except Exception as e:
        logger.error("Error iniciando MQTT: %s", e)

def abrir_navegador():
    webbrowser.open("http://127.0.0.1:8000/")

if __name__ == "__main__":
    t = threading.Thread(target=start_background_services, daemon=True)
    t.start()
    threading.Timer(1.5, abrir_navegador).start()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
