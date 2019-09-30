import datetime, os
from query_time import WEEKDAY

DAY_FORMAT = '{:^5}'

def process_show(*args):
    this_dir, _ = os.path.split(__file__)
    if 'yourself' in args:
        file_path = os.path.join(this_dir, 'data', 'ada.dat')
        print open(file_path, 'r').read()
    elif 'calendar' in args:
        print_calendar()
    else:
        print('Unable to show...')

def print_calendar():
    today = datetime.date.today()
    rows2print = []
    s = ''
    for d in WEEKDAY:
        s = s + DAY_FORMAT.format(d)
    rows2print.append(s)
    s = ''
    month = today.month
    day_ptr = datetime.date(today.year, today.month, 1)
    wd = 0
    while day_ptr.month == month:
        if day_ptr.weekday() != wd:
            s = s + DAY_FORMAT.format('')
        else:
            if wd == 0 and len(s) > 0:
                rows2print.append(s)
                s = ''
            if day_ptr == today:
                s = s + DAY_FORMAT.format('*' + str(day_ptr.day) + '*')
            else:
                s = s + DAY_FORMAT.format(day_ptr.day)
            day_ptr = day_ptr + datetime.timedelta(days = 1)
        wd = (wd + 1) % 7
    if len(s) > 0:
        rows2print.append(s)
    for row in rows2print:
        print(row)
