# Value Investing Platform

Production-focused financial analytics platform inspired by Benjamin Graham and Warren Buffett style research.

## Architecture

```
value-investing-platform/
├── app/                # FastAPI app + service layer
├── data_pipeline/      # yfinance collection + normalization + storage
├── screens/            # Graham/Buffett metrics and screen logic
├── database/           # SQLAlchemy models and session setup
├── automation/         # APScheduler jobs
├── tests/              # Unit tests
├── requirements.txt
├── .env.example
└── README.md
```

## Features

- Ingests profile, prices, financial statements, analyst, insider, and news data from `yfinance`.
- Normalizes financial statements into tidy schema: `ticker | statement | line_item | period | value`.
- Computes value metrics: P/E, P/B, current ratio, debt-to-equity, Graham number, margin of safety, ROE, ROIC, FCF, FCF yield, margins.
- Pure function screeners: Graham, Buffett, and combined ranking.
- FastAPI routes:
  - `GET /health`
  - `GET /ticker/{symbol}`
  - `GET /ticker/{symbol}/financials`
  - `GET /screen/graham`
  - `GET /screen/buffett`
  - `GET /screen/combined`
- APScheduler automation jobs for daily updates, metric recomputation, and screening.

## Setup

```bash
python -m venv .venv
.\.venv\Scripts\activate.ps1
pip install -r requirements.txt
```

## Run API

```bash
uvicorn app.main:app --reload
```

## Run Tests

```bash
pytest -q
```

## Run Scheduler

```bash
python -m automation.scheduler
```
