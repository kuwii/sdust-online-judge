# -*- coding: utf-8 -*-
from requests.auth import HTTPBasicAuth

from sqlalchemy.orm import sessionmaker
from data_updater.models import server as server_models

from config import CLIENT_SETTINGS

from .utils import request_data, timestamp_to_date_str, updated_request, timestamp_cur, print_json
from .cache import update_cache

url = CLIENT_SETTINGS['root_url'].rstrip('/') + '/' + CLIENT_SETTINGS['category_url'].lstrip('/')
category_problem_url = CLIENT_SETTINGS['category_problem_url'].rstrip('/')
username = CLIENT_SETTINGS['username']
password = CLIENT_SETTINGS['password']
auth = HTTPBasicAuth(username, password)
cache_name = 'category_updater_cache'


Session = sessionmaker(bind=server_models.engine)
session = Session()


def request_category_list(request_url):
    return request_data(url=request_url, auth=auth)


def request_category_problem_list(request_url):
    return request_data(url=request_url, auth=auth)


def write_category(cat_json):
    cat = session.query(server_models.Category).filter_by(id=cat_json['id']).first()
    if cat is None:
        cat_model = server_models.Category(id=cat_json['id'],
                                           title=cat_json['title'],
                                           introduction=cat_json['introduction'],
                                           source=cat_json['source'],
                                           author=cat_json['author'],
                                           number_problem=cat_json['number_problem'])
        session.add(cat_model)
        print('created cat %s: %s' % (cat_json['id'], cat_json['title']))
    else:
        cat.title = cat_json['title']
        cat.introduction = cat_json['introduction']
        cat.source = cat_json['source']
        cat.author = cat_json['author']
        cat.number_problem = cat_json['number_problem']
        print('updated env %s: %s' % (cat_json['id'], cat_json['title']))
    session.commit()


def write_category_problems(cat_id, cp_json):
    cp = session.query(
        server_models.CategoryProblemRelation).filter_by(id=cp_json['id']).first()
    problem = session.query(
        server_models.Problem).filter_by(id=cp_json['problem']['id']).first()
    if problem is None:
        if cp is not None:
            session.delete(cp)
    elif cp is None:
        cat_model = server_models.CategoryProblemRelation(id=cp_json['id'],
                                                          category_id=cat_id,
                                                          problem_id=cp_json['problem']['id'],
                                                          directory=cp_json['directory'])
        session.add(cat_model)
        print('created cat_problem %s: %s' % (cp_json['id'], cp_json['problem']['title']))
    else:
        cp.category_id = cat_id,
        cp.problem_id = cp_json['problem']['id']
        cp.directory = cp_json['directory']
        print('updated cat_problem %s: %s' % (cp_json['id'], cp_json['problem']['title']))
    session.commit()


def update_category(cat_json):
    write_category(cat_json)
    cat_id = int(cat_json['id'])
    request_url = url.rstrip('/') + ('/%s/' % (cat_json['id'])) + category_problem_url + '/'
    while request_url is not None:
        chance_left = 3
        cp_list = None
        while cp_list is None and chance_left > 0:
            print('requesting %s, tried %s ......' % (request_url, 3-chance_left))
            cp_list = request_category_problem_list(request_url)
            chance_left -= 1
        if cp_list is None:
            request_url = None
        else:
            for cp in cp_list['results']:
                write_category_problems(cat_id, cp)
            request_url = cp_list['next']


def update_categories(update_all=False):
    time = timestamp_cur()
    request_url = url if update_all else updated_request(url, cache_name)
    while request_url is not None:
        chance_left = 3
        cat_list = None
        while cat_list is None and chance_left > 0:
            print('requesting %s, tried %s ......' % (request_url, 3-chance_left))
            cat_list = request_category_list(request_url)
            chance_left -= 1
        if cat_list is None:
            request_url = None
        else:
            for c in cat_list['results']:
                update_category(c)
            request_url = cat_list['next']
    update_cache(cache_name, time)
