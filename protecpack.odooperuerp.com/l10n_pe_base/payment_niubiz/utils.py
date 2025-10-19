
from datetime import datetime

def txt_to_datetime(txt):
    date_time = datetime.strptime(txt, "%y%m%d%H%M%S")
    return date_time