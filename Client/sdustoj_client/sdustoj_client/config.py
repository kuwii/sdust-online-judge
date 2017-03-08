# 数据库的设定
PG_SETTINGS = {
    'host': 'localhost',
    'port': '5432',
    'db': 'sdustoj_client',
    'user': 'korosensei',
    'password': 'big_boss'
}

REDIS_SETTINGS = {
    'host': '192.168.221.132',
    'port': '6379',
    'password': 'hust',
    'db': 1
}

# 系统初始根用户信息，密码仅在首次创建用户时设定
# 当日后无需检查时，可将此项设为None，则每次同步数据库时不会检查
INIT_USER_SETTINGS = {
    'username': 'korosensei',
    'password': 'big_boss',
    'name': '殺せんせー'
}
