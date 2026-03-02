# Value Investing Platform (Phase 1: Backend)

## Setup

```bash
python -m venv .venv
.venv\Scripts\Activate
pip install -r backend/requirements.txt
```

## Run API

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

- `GET /api/health`
- `GET /api/ticker/{symbol}/all`
