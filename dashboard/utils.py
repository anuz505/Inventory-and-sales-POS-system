from .stats import periods, get_start_date
from datetime import datetime, date, timedelta


def get_startdate_from_request(request, default_period="month"):
    period = request.query_params.get("period")
    from_date = request.query_params.get("from_date")

    if period:
        mapped_period = periods.get(period, default_period)

        if mapped_period == "today":
            start_date = datetime.now().date()
        else:
            start_date = get_start_date(mapped_period)

        return start_date, period

    elif from_date:
        start_date = datetime.fromisoformat(from_date)
        return start_date, "custom"

    else:
        start_date = get_start_date(default_period)
        return start_date, None
