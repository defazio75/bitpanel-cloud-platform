# utils/performance_aggregator.py
import datetime
from collections import defaultdict
from utils.firebase_db import load_trade_logs, save_performance_summary


def aggregate_trades_by_day(user_id, token, mode):
    trade_logs = load_trade_logs(user_id, token, mode)
    daily_aggregates = {}

    for date_str, trades in trade_logs.items():
        summary = defaultdict(lambda: defaultdict(float))
        summary["summary"]["total_trades"] = 0
        summary["summary"]["total_profit"] = 0.0

        for time_key, trade in trades.items():
            coin = trade.get("coin")
            strategy = trade.get("strategy")
            profit = float(trade.get("profit_usd", 0.0))
            amount = float(trade.get("amount", 0.0))

            summary[coin][strategy] += profit
            summary[coin][f"{strategy}_volume"] += amount
            summary[coin]["total_profit"] += profit
            summary[coin]["total_volume"] += amount
            summary[coin]["total_trades"] += 1

            summary["summary"]["total_trades"] += 1
            summary["summary"]["total_profit"] += profit

        daily_aggregates[date_str] = summary
        save_performance_summary(user_id, token, mode, date_str, summary)

    return daily_aggregates


def aggregate_periodic_summary(daily_aggregates, period="weekly"):
    bucket = defaultdict(lambda: defaultdict(float))

    for date_str, daily_data in daily_aggregates.items():
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

        if period == "weekly":
            bucket_key = f"W{date_obj.isocalendar()[1]}-{date_obj.year}"
        elif period == "monthly":
            bucket_key = f"{date_obj.year}-{date_obj.month:02d}"
        elif period == "ytd":
            bucket_key = f"YTD-{date_obj.year}"
        else:
            continue

        for coin, coin_data in daily_data.items():
            for k, v in coin_data.items():
                bucket[bucket_key][f"{coin}_{k}"] += v

    return dict(bucket)


# === Entry Point for Aggregation Task ===
def run_aggregation(user_id, token, mode):
    print("🔄 Running daily trade log aggregation...")
    daily = aggregate_trades_by_day(user_id, token, mode)

    print("📅 Aggregating weekly summary...")
    weekly = aggregate_periodic_summary(daily, period="weekly")
    for week, summary in weekly.items():
        save_performance_summary(user_id, token, mode, f"weekly/{week}", summary)

    print("📆 Aggregating monthly summary...")
    monthly = aggregate_periodic_summary(daily, period="monthly")
    for month, summary in monthly.items():
        save_performance_summary(user_id, token, mode, f"monthly/{month}", summary)

    print("📈 Aggregating YTD summary...")
    ytd = aggregate_periodic_summary(daily, period="ytd")
    for ytd_key, summary in ytd.items():
        save_performance_summary(user_id, token, mode, f"ytd/{ytd_key}", summary)

    print("✅ Aggregation complete.")
