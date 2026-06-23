import re
from datetime import datetime, timedelta

def parse_duration(duration_str):

    pattern = re.compile(
        r"^P(?:(?P<days>\d+)D)?"
        r"(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?$"
    )
    match = pattern.match(duration_str)

    if not match:
        raise ValueError(f"Invalid ISO 8601 duration: {duration_str}")

    total_duration = timedelta(
        days=int(match.group("days") or 0),
        hours=int(match.group("hours") or 0),
        minutes=int(match.group("minutes") or 0),
        seconds=int(match.group("seconds") or 0),
    )
                         
    return total_duration


def transform_data(row):

    duration_timedelta = parse_duration(row['Duration'])

    row['Duration'] = (datetime.min + duration_timedelta).time()

    row['Video_Type'] = 'Shorts' if duration_timedelta.total_seconds() <= 60 else 'Normal'

    return row


def transform_date(row):
    return transform_data(row)

