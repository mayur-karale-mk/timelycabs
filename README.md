# TimelyCabs FastAPI Project

A FastAPI application for TimelyCabs with a simple root endpoint.

## Setup

### 1. Virtual Environment
The virtual environment is already created and activated. If you need to recreate it:

```bash
# Create virtual environment
python3 -m venv fast_api_env

# Activate virtual environment
source fast_api_env/bin/activate  # On Linux/Mac
# or
fast_api_env\Scripts\activate     # On Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

### Development Server
```bash
# Run with the run.py file
python run.py

# Or run with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint

## Interactive API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
timelycabs/
├── app/
│   ├── __init__.py
│   └── main.py              # Main FastAPI application
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── fast_api_env/           # Virtual environment directory
```

## Features

- FastAPI framework with automatic API documentation
- CORS middleware for cross-origin requests
- Health check endpoint
- Simple and clean structure
- Hot reload for development
