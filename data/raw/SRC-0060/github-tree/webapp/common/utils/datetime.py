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
    date.replace(hour=0, minute=0, second=0, microsecond=0),
    date.replace(hour=23, minute=59, second=59, microsecond=999999),
  )


def get_today_start():
  return get_day_range()[0]


def get_today_end():
  return get_day_range()[1]
