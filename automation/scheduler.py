"""APScheduler setup for recurring platform jobs."""

from __future__ import annotations

from apscheduler.schedulers.blocking import BlockingScheduler

from automation.jobs import recompute_metrics, run_undervalued_screen, update_tickers


def start_scheduler(tickers: list[str]) -> None:
    scheduler = BlockingScheduler()
    scheduler.add_job(update_tickers, "interval", minutes=1, args=[tickers], id="update_data_dev")
    scheduler.add_job(recompute_metrics, "cron", hour=19, minute=0, args=[tickers], id="recompute_metrics_daily")
    scheduler.add_job(run_undervalued_screen, "cron", hour=20, minute=0, args=[tickers], id="screen_daily")
    scheduler.start()


if __name__ == "__main__":
    start_scheduler(["AAPL", "MSFT", "GOOGL"])
