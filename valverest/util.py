from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import mktime

gmt_j2koffset = 946764000
hst_j2koffset = 946728000

def date_to_j2k(d, hst=False):
    """
    Given a date, return the J2KSeconds value
    d   -- Date to convert
    hst -- Timezone the date is in
    """
    if isinstance(d, str):
        d = datetime.strptime(d, "%Y-%m-%d %H:%M:%S")

    if hst:
        return (mktime(d.timetuple())) - hst_j2koffset
    else:
        return (mktime(d.timetuple())) - gmt_j2koffset

def j2k_to_date(j2k, hst=False):
    """
    Return the date for the passed in j2k value.
    j2k -- J2K value to parse
    hst -- Requested timezone
    """
    if hst:
        return datetime.fromtimestamp(j2k + hst_j2koffset)
    else:
        return datetime.fromtimestamp(j2k + gmt_j2koffset)

def create_date_from_input(start, end, hst):
    if start.startswith('-'):
        s = create_relative_date(start)
    else:
        if len(start) == 4:
            start += '0101000000000'
        elif len(start) == 8:
            start += '000000000'
        elif len(start) == 12:
            start += '00000'
        s = datetime.strptime(start, "%Y%m%d%H%M%S%f")
    if end == 'now':
        e = datetime.now() if hst else datetime.utcnow()
    else:
        if len(end) == 4:
            end += '1231235959999'
        elif len(end) == 8:
            end += '235959999'
        elif len(end) == 12:
            end += '59999'
        e = datetime.strptime(end, "%Y%m%d%H%M%S%f")
    return s, e

def create_relative_date(s):
    period = s[-1:]
    time = int(s[1:-1]) * -1
    if period == 's':
        label = 'seconds'
    elif period == 'i':
        label = 'minutes'
    elif period == 'h':
        label = 'hours'
    elif period == 'd':
        label = 'days'
    elif period == 'w':
        label = 'weeks'
    elif period == 'm':
        label = 'months'
    elif period == 'y':
        label = 'years'
    kwargs = { label: time }
    return datetime.now() + relativedelta(**kwargs)

def clean_input(arg):
    for key,val in arg.iteritems():
        arg[key] = val.strip() if isinstance(val, basestring) else val
    return arg

def str_to_date(s):
    return mktime(datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f").timetuple())
