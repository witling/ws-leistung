def dateformat(date):
    from datetime import datetime
    import calendar

    day = date.day
    month = calendar.month_name[date.month]
    year = date.year

    return "{}. {} {}".format(day, month, year)
