import csv
from django.http import HttpResponse
import datetime


def generate_filename(table_name):
    today = datetime.date.today().strftime("%Y-%m-%d")
    return f"{table_name}_report_{today}.csv"


def get_data(startdate, model, enddate=None):
    headers = [
        field.name
        for field in model._meta.get_fields()
        if field.concrete and not field.many_to_many
    ]
    if enddate:
        query_set = model.objects.all().filter(
            created_at__gte=startdate, created_at__lte=enddate
        )
    else:
        query_set = model.objects.all().filter(created_at__gte=startdate)
    rows = []
    for obj in query_set:
        row = []
        for header in headers:
            value = getattr(obj, header)
            if hasattr(value, "name"):
                value = value.name
            elif hasattr(value, "__str__"):
                value = str(value)
            row.append(value)
        rows.append(row)
    return {"header": headers, "rows": rows}


def generate_csv(filename, model, startdate, enddate=None):
    raw_data = get_data(
        startdate,
        model,
        enddate,
    )
    response = HttpResponse(content_type="text/csv")
    response["Access-Control-Expose-Headers"] = "Content-Disposition"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(raw_data["header"])
    for row in raw_data["rows"]:
        writer.writerow(row)

    return response
