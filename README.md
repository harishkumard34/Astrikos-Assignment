# Equipment Monitoring Service

This is a complete solution for monitoring a fleet of physical equipment through sensor data. It ingests continuous telemetry, stores it, and surfaces critical anomalies to an operator via a live dashboard.

## Architecture

The system is divided into three components:
1. **Data Generator (`generator/main.py`)**: Simulates a small fleet of equipment (e.g., pumps, cooling units). It intentionally generates messy data, including normal fluctuations, sudden noise spikes, sensor faults (0.0 readings), and gradual degradation over time.
2. **Backend Service (`backend/`)**: A FastAPI application that ingests telemetry via `POST /ingest`. It stores historical data in a local SQLite database and runs an in-memory analysis engine to detect anomalies.
3. **Frontend Dashboard (`frontend/`)**: A modern, dark-themed HTML/JS/CSS interface that polls the backend and provides operators with real-time status and alerts.

## How we handle "Messy Data"

The assignment specifically asks to handle messy sensor data. The analysis engine in `backend/main.py` handles this in three ways:
- **Noise / Spikes**: It uses a sliding window (moving average) of the last 5 readings. If a sudden reading is drastically higher than the moving average while previous readings were normal, it is flagged as noise and ignored.
- **Sensor Faults**: If a reading drops to exactly `0.0`, the system instantly flags it as a `SENSOR_FAULT` rather than assuming the machine is broken.
- **Gradual Failure**: If the sliding window detects a strict and consistent increase in a metric (e.g., temperature) over a threshold, it flags it as a `GRADUAL_FAILURE` to provide an early warning before the machine actually breaks.

## How to Run

### Prerequisites
- Python 3.8+
- Modern Web Browser

### Setup
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

### 1. Start the Backend
```bash
uvicorn backend.main:app --reload
```
The backend will run on `http://127.0.0.1:8000`.

### 2. Start the Data Generator
Open a new terminal, activate the virtual environment, and run:
```bash
python generator/main.py
```
You will see logs of fake sensor data being sent to the backend.

### 3. Open the Dashboard
Simply open `frontend/index.html` in your web browser. You will see the live status of the machines and any alerts popping up on the right side.
