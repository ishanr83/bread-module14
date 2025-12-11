# BREAD Calculator - Module 14

## GitHub Repository
https://github.com/ishanr83/bread-module14

## Docker Hub
https://hub.docker.com/r/ishanr83/bread-calculator

## Run Locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run Tests
```bash
pytest tests/ -v
```

## API Endpoints
- POST /api/register - Register user
- POST /api/login - Login user
- GET /api/calculations - Browse all
- GET /api/calculations/{id} - Read one
- PUT /api/calculations/{id} - Edit
- POST /api/calculations - Add new
- DELETE /api/calculations/{id} - Delete
