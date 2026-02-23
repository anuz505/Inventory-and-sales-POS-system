from django.utils import timezone
from datetime import datetime, timedelta
from .stats import periods


def get_start_date(period: str):
    now = timezone.now()
    if period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == "3months":
        month = (now.month - 3) % 12 or 12
        year = now.year if now.month > 3 else now.year - 1
        start = now.replace(
            year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        end = now
    elif period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == "year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == "12months":
        start = (now - timedelta(days=365)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = now

    else:
        raise ValueError("Invalid period. Use 'month', '3months', or 'year'.")
    return start, end


def get_prev_period(start, end):
    duration = end - start
    prev_end = start
    prev_start = start - duration
    return prev_start, prev_end


def get_period_range_from_request(request, default_period="12months"):
    now = timezone.now()

    period = request.query_params.get("period")
    from_date = request.query_params.get("from_date")
    to_date = request.query_params.get("to_date")

    if period:
        mapped_period = periods.get(period, default_period)
        start_date, end_date = get_start_date(mapped_period)
        return start_date, end_date, period

    if from_date:
        start_date = datetime.fromisoformat(from_date)
        start_date = timezone.make_aware(start_date)

        if to_date:
            end_date = datetime.fromisoformat(to_date)
            end_date = timezone.make_aware(end_date)
        else:
            end_date = now

        return start_date, end_date, "custom"

    start_date, end_date = get_start_date(default_period)
    # print(f"Period: {period}, Start: {start_date}, End: {end_date}")
    return start_date, end_date, default_period
