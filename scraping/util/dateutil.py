from datetime import datetime, timezone


def str_of_now_Ymd():
    """Get current date as string in YYYYMMDD format.

    Returns:
        str: current date in YYYYMMDD format
    """
    return datetime.date.today().strftime('%Y%m%d')

def str_of_now_YmdHMS():
    """Get current datetime as string in YYYYMMDD24HHMMSS format.

    Returns:
        str: current datetime in YYYYMMDD24HHMMSS format
    """
    return datetime.now().strftime('%Y%m%d%H%M%S')

def str_of_dt_dmYHMS(dt):
    """Get string of given datetime in DD-MM-YYYY 24HH:MM:SS format.

    Args:
        dt (datetime): Datetime object to convert to string.

    Returns:
        str: string of given datetime in DD-MM-YYYY 24HH:MM:SS format
    """
    return datetime.strftime(dt, '%d-%m-%Y %H:%M:%S')

def dt_of_now():
    """Get current datetime as datetime.

    Returns:
        datetime: current datetime without timezone info
    """
    return datetime.now()

def dt_of_utcnow():
    """Get current UTC datetime as datetime.

    Returns:
        datetime: current UTC datetime without timezone info
    """
    return datetime.now(timezone.utc)

def str_of_utcnow_YmdHMS():
    """Get current UTC datetime as datetime.

    Returns:
        datetime: current UTC datetime without timezone info
    """
    return dt_of_utcnow().strftime('%Y-%m-%d %H:%M:%S %Z')
