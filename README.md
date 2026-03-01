# Value Investing Platform (Starter)

This repository contains a starter backend for your idea:

- Pull broad company + market data from **yfinance**.
- Expose data through a web API.
- Run an automated value screener inspired by **Buffett/Graham** principles.

## What is implemented

### 1) API endpoint coverage

`GET /tickers/{ticker}/snapshot` includes:

- `profile` (company metadata, market cap, sector, etc.)
- `prices.daily` + `prices.intraday`
- `financials` (income statement, balance sheet, cash flow; yearly + quarterly where available)
- `events` (earnings dates + calendar + dividends)
- `analyst` (recommendations, targets, estimates)
- `insider` (purchases + transactions)
- `news`

### 2) Undervalued stock screener

`GET /screen/undervalued?tickers=AAPL&tickers=GOOGL`

A rules-based score checks:

- Forward P/E
- Price-to-book
- Profit margins
- Return on equity
- Debt-to-equity
- Free cash flow
- Dividend presence

Output includes score, classification, and which checks passed.

## Run locally

### 1) Create virtual env

```bash
python -m venv .venv
```

### 2) Activate virtual env

**macOS/Linux (bash/zsh):**

```bash
source .venv/bin/activate
```

**Windows Command Prompt (cmd.exe):**

```bat
.venv\Scripts\activate.bat
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install -e . pytest
```

### 4) Start API server

```bash
uvicorn value_investing_platform.api:app --reload
```

Open interactive docs at: `http://127.0.0.1:8000/docs`

## Test locally

### Unit tests

```bash
python -m pytest -q
```

### Optional smoke test (API running in another terminal)

```bash
curl "http://127.0.0.1:8000/health"
curl "http://127.0.0.1:8000/screen/undervalued?tickers=AAPL&tickers=MSFT"
```

## Suggested next steps

1. Add caching (Redis/Postgres) so automation doesn't repeatedly hit Yahoo.
2. Store daily snapshots to build backtests and trend charts.
3. Split score into "Graham score" and "Buffett quality score".
4. Add a scheduler (cron/Celery/GitHub Actions) to run screening automatically.
5. Add a frontend dashboard (Next.js/React) to visualize score history and metrics.
