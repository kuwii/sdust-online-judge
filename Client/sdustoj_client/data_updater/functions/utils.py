import json
import requests
from .cache import read_cache
from datetime import datetime
from time import mktime


def updated_request(url, cache_name):
    cache_time = read_cache(cache_name)
    if cache_time is not None:
        last_time = timestamp_to_date_str(cache_time)
        url = url.rstrip('/') + '/?update_time_gte=%s' % (last_time,)
    return url


def timestamp_cur():
    return mktime(datetime.now().timetuple())


def request_data(url, params=None, **kwargs):
    r = requests.get(url, params, **kwargs)
    if r.status_code == 200:
        return r.json()
    else:
        return None


def return_none(*args, **kwargs):
    return None


def timestamp_to_date_str(timestamp):
    dt = datetime.utcfromtimestamp(timestamp)

    return dt.strftime('%Y-%m-%d %H:%M:%S')


def str_to_datetime(str):
    return datetime.strptime(str, '%Y-%m-%dT%H:%M:%S.%fZ')


def print_json(data):
    print(json.dumps(data, sort_keys=True, indent=2))
