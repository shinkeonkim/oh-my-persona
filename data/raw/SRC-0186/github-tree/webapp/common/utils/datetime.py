from django.utils import timezone


def get_today_range():
    now = timezone.now()
    return (
        now.replace(hour=0, minute=0, second=0, microsecond=0),
        now.replace(hour=23, minute=59, second=59, microsecond=999999),
    )


def get_today_start():
    return get_today_range()[0]


def get_today_end():
    return get_today_range()[1]
