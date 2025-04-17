from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
import subprocess

app = FastAPI()

# Use absolute paths for static and templates directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "frontend", "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

DATA_DIR = os.path.join(BASE_DIR, "data")
MOTHERBOARDS_FILE = os.path.join(DATA_DIR, "motherboards.json")

os.makedirs(DATA_DIR, exist_ok=True)

# Load or initialize motherboards data
def load_motherboards():
    if not os.path.exists(MOTHERBOARDS_FILE):
        with open(MOTHERBOARDS_FILE, "w") as f:
            json.dump({}, f)
    with open(MOTHERBOARDS_FILE, "r") as f:
        return json.load(f)

def save_motherboards(data):
    with open(MOTHERBOARDS_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    motherboards = load_motherboards()
    return templates.TemplateResponse("index.html", {"request": request, "motherboards": motherboards})

@app.post("/add_mapping")
def add_mapping(motherboard: str = Form(...), slot: str = Form(...), bus_id: str = Form(...), uuid: str = Form(...)):
    data = load_motherboards()
    if motherboard not in data:
        data[motherboard] = {}
    data[motherboard][slot] = {"bus_id": bus_id, "uuid": uuid}
    save_motherboards(data)
    return JSONResponse({"success": True})

@app.get("/get_mappings/{motherboard}")
def get_mappings(motherboard: str):
    data = load_motherboards()
    return data.get(motherboard, {})

@app.get("/get_all_motherboards")
def get_all_motherboards():
    return load_motherboards()

# Placeholder for photo upload (advanced)
@app.post("/upload_photo")
def upload_photo(motherboard: str = Form(...), file: UploadFile = File(...)):
    photo_dir = os.path.join(DATA_DIR, "photos")
    os.makedirs(photo_dir, exist_ok=True)
    file_location = os.path.join(photo_dir, f"{motherboard}.jpg")
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    return {"filename": file_location}

# Placeholder for troubleshooting dashboard (to be implemented)
@app.get("/troubleshoot/{motherboard}")
def troubleshoot(motherboard: str):
    # TODO: Parse nvidia-smi output and return error/warning info
    return {"status": "Not implemented yet"}

@app.get("/detect_gpus/{motherboard}")
def detect_gpus(motherboard: str):
    data = load_motherboards()
    if motherboard not in data:
        raise HTTPException(status_code=404, detail="Motherboard not found")
    board_data = data[motherboard]
    slots = board_data.get('slots', {})
    # Run nvidia-smi and parse output (get both details and names)
    try:
        result = subprocess.run([
            'nvidia-smi',
            '--query-gpu=index,gpu_bus_id,serial,uuid,name',
            '--format=csv,noheader'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"nvidia-smi failed: {e}")
    detected = []
    for line in result.stdout.strip().split('\n'):
        parts = [p.strip() for p in line.split(',')]
        if len(parts) != 5:
            continue
        gpu_index, bus_id, serial, uuid, name = parts
        detected.append({
            'gpu_index': gpu_index.replace('GPU ', ''),
            'bus_id': bus_id,
            'serial': serial,
            'uuid': uuid,
            'name': name
        })
    def normalize(busid):
        if ',' in busid:
            busid = busid.split(',', 1)[-1]
        return busid.strip().lower()
    slot_to_gpu = {}
    for slot, info in slots.items():
        if not isinstance(info, dict) or 'bus_id' not in info:
            slot_to_gpu[slot] = None
            continue
        slot_bus_id = normalize(info['bus_id'])
        match = next((g for g in detected if normalize(g['bus_id']) == slot_bus_id), None)
        if match:
            slot_to_gpu[slot] = match
        else:
            slot_to_gpu[slot] = None
    return slot_to_gpu
