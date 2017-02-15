from datetime import datetime


def print_log(*args, **kwargs):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('[%s] ' % (dt,), end='')
    print(*args, **kwargs)
