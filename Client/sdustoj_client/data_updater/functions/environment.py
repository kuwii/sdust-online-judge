# -*- coding: utf-8 -*-
from requests.auth import HTTPBasicAuth

from sqlalchemy.orm import sessionmaker
from data_updater.models import server as server_models

from config import CLIENT_SETTINGS

from .utils import request_data, updated_request, timestamp_cur
from .cache import update_cache

url = CLIENT_SETTINGS['root_url'].rstrip('/') + '/' + CLIENT_SETTINGS['environment_url'].lstrip('/')
username = CLIENT_SETTINGS['username']
password = CLIENT_SETTINGS['password']
auth = HTTPBasicAuth(username, password)
cache_name = 'environment_updater_cache'


Session = sessionmaker(bind=server_models.engine)
session = Session()


def request_environment_list(request_url):
    return request_data(url=request_url, auth=auth)


def write_environment(env_json):
    env = session.query(server_models.Environment).filter_by(id=env_json['id']).first()
    if env is None:
        env_model = server_models.Environment(id=env_json['id'],
                                              name=env_json['name'])
        session.add(env_model)
        print('created env %s: %s' % (env_json['id'], env_json['name']))
    else:
        env.name = env_json['name']
        print('updated env %s: %s' % (env_json['id'], env_json['name']))
    session.commit()


def update_environments(update_all=False):
    time = timestamp_cur()
    request_url = url if update_all else updated_request(url, cache_name)
    while request_url is not None:
        chance_left = 3
        env_list = None
        while env_list is None and chance_left > 0:
            print('requesting %s, tried %s ......' % (request_url, 3-chance_left))
            env_list = request_environment_list(request_url)
            chance_left -= 1
        if env_list is None:
            request_url = None
        else:
            for e in env_list['results']:
                write_environment(e)
            session.commit()
            request_url = env_list['next']
    update_cache(cache_name, time)
