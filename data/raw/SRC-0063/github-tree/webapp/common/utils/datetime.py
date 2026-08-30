from django.utils import timezone


def get_current_datetime():
    return timezone.now()


def get_today_date():
    return timezone.localdate()


def get_current_year():
    return get_current_datetime().year


def get_current_month():
    return get_current_datetime().month


def get_current_day():
    return get_current_datetime().day


def get_day_range(date=None):
    if date is None:
        date = get_today_date()

    return (
        timezone.datetime.combine(date, timezone.datetime.min.time()),
        timezone.datetime.combine(date, timezone.datetime.max.time()),
    )


def get_today_start():
    return get_day_range()[0]


def get_today_end():
    return get_day_range()[1]
