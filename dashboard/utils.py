from django.utils import timezone
from datetime import datetime
from .stats import periods, get_start_date


def get_period_range_from_request(request, default_period="month"):
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
    return start_date, end_date, default_period
