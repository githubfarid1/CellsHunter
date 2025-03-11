import time
from datetime import datetime, timedelta

import ntplib
from pytz import timezone


def get_sync_time():
    client = ntplib.NTPClient()
    # server = 'pool.ntp.org'
    server = "time.nrc.ca"
    # resp = client.request(server, version=3)
    resp = client.request(server, version=4)
    return resp.tx_time, resp.offset


def get_lcd_time_with_timezone(_time, tz: str):
    """
    :return:
    str - time for qt5
    str - time offset
    float - +0 timestamp
    """
    time_zone = timezone(tz)  # select timezone
    # tx_time = datetime.utcfromtimestamp(_time)  # convert timestamp to datetime object
    tx_time = datetime.fromtimestamp(_time, tz=time_zone)
    tx_time_with_tz = tx_time.astimezone(time_zone)  # change +0 to +TZ
    tx_time_w_tz_str = tx_time_with_tz.strftime('%H:%M:%S.%f')[:-3]  # Apply time format for qt clock
    return tx_time_w_tz_str, tx_time_with_tz


def get_time_with_timezone_and_offset(tz: str, offset: float):
    _dt = datetime.now(timezone(tz))
    _dt = _dt + timedelta(seconds=offset)
    _dt = _dt.strftime('%H:%M:%S.%f')[:-3]
    return _dt


def get_time_object_with_timezone_and_offset(tz: str, offset: float):
    _dt = datetime.now(timezone(tz))
    _dt = _dt + timedelta(seconds=offset)
    _dt = _dt.strftime('%H:%M:%S.%f')
    _dt = datetime.strptime(_dt, '%H:%M:%S.%f')
    return _dt


def get_time_from_params(par: dict):
    return datetime.strptime(f'{par["hour"]}:{par["minute"]}:{par["second"]}', '%H:%M:%S')


def get_current_day_with_timezone_and_offset(tz: str, offset: float):
    _dt = datetime.now(timezone(tz))
    _dt = _dt + timedelta(seconds=offset)
    return _dt


def run_by_time(f):
    """
    run by selected time
    :return:
    """

    def wrapper(*args):

        while not args[0].stop:

            if args[0].start_at_object <= get_time_object_with_timezone_and_offset(args[0].tz, args[0].offset):
                break
            else:
                args[0].change_app_status.emit('Idle. Waiting right time')
                time.sleep(0.0001)

        if args[0].stop:
            args[0].stop_thread.emit()
            return
        else:
            args[0].change_app_status.emit('Start Hunting..')

        return f(*args)

    return wrapper


def get_request_time(f):
    def wrapper(*args):
        start_time = time.time()

        f(*args)

        return round(time.time() - start_time, 3)

    return wrapper


if __name__ == '__main__':
    start_at = {
        'hour': 4,
        'minute': 4,
        'second': 4,
    }
    d = get_time_from_params(start_at)
    t = get_time_object_with_timezone_and_offset(tz='US/Eastern', offset=0)
    # breakpoint()
    print(t)