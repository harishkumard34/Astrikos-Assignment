# Equipment Monitoring Service

This is a complete solution for monitoring a fleet of physical equipment through sensor data. It ingests continuous telemetry, stores it, and surfaces critical anomalies to an operator via a live dashboard.

## Architecture

The system is divided into three components:
1. **Data Generator (`generator/main.py`)**: Simulates a small fleet of equipment. It intentionally generates messy data, including normal fluctuations, sudden noise spikes, sensor faults (0.0 readings), and gradual degradation over time.
2. **Backend Service (`backend/`)**: A FastAPI application that ingests telemetry. It stores historical data in a local SQLite database and runs an in-memory analysis engine to detect anomalies. It also serves the frontend dashboard.
3. **Frontend Dashboard (`frontend/`)**: A modern, light-themed HTML/JS/CSS interface that polls the backend and provides operators with real-time status and alerts.

## How we handle "Messy Data"

- **Noise / Spikes**: Uses a sliding window (moving average) of the last 5 readings. If a sudden reading is drastically higher than the moving average while previous readings were normal, it is flagged as noise and ignored.
- **Sensor Faults**: If a reading drops to exactly `0.0`, the system instantly flags it as a `SENSOR_FAULT`.
- **Gradual Failure**: If the sliding window detects a strict and consistent increase in a metric over a threshold, it flags it as a `GRADUAL_FAILURE` to provide an early warning.

## How to Run Locally (Windows)

Assuming your python virtual environment is setup (`python -m venv venv`) and dependencies are installed (`pip install -r requirements.txt`), you can run the project using just two commands. We use direct script paths to bypass any PowerShell Execution Policy issues.

**Step 1: Start the Backend Server**
Open a terminal in the project root folder and run:
```bash
.\venv\Scripts\python -m uvicorn backend.main:app --reload
```

**Step 2: Start the Data Generator**
Open a **new** terminal in the project root folder and run:
```bash
.\venv\Scripts\python generator\main.py
```

**Step 3: View the Dashboard**
Open your web browser (Chrome/Edge) and go to:
👉 **http://127.0.0.1:8000**
