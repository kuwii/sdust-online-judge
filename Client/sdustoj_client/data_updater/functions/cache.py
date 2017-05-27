# -*- coding: utf-8 -*-
def read_cache(cache_name):
    try:
        f = open(cache_name, 'r')
        time = float(f.readline())
        f.close()
    except FileNotFoundError:
        time = None
    return time


def update_cache(cache_name, timestamp):
    f = open(cache_name, 'w')
    f.write(str(timestamp))
    f.close()
