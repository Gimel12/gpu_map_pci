# GPU Location Board

A FastAPI-based web application to map and visualize GPU logical identifiers (as shown by nvidia-smi) to their physical motherboard slots. Features include:

- Mapping of GPU bus IDs/UUIDs to physical PCIe slots for various motherboards
- Simple web interface for visualization and management
- JSON-based backend for data storage
- (Planned) Photo upload for annotation
- (Planned) Auto-detection of motherboard model
- (Planned) Troubleshooting dashboard showing nvidia-smi errors/warnings

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
3. Open your browser to `http://localhost:8000`

---

## Project Structure
- `main.py`: FastAPI backend
- `frontend/`: HTML/JS frontend
- `data/`: JSON files storing mappings

---

## Roadmap
- [x] Initial FastAPI backend
- [x] JSON storage for mappings
- [ ] Frontend for mapping/visualization
- [ ] Photo upload & annotation
- [ ] Motherboard auto-detection
- [ ] Troubleshooting dashboard
