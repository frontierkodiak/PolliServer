import datetime

from PolliServer.constants import *


# Determine the date format and parse accordingly
def parse_date_string(date_string):
    DATE_FORMAT_STRING = '%Y-%m-%d'
    if 'T' in date_string:
        # Full datetime string
        return datetime.datetime.strptime(date_string, DATETIME_FORMAT_STRING)
    else:
        # Date-only string
        return datetime.datetime.strptime(date_string, DATE_FORMAT_STRING).date()