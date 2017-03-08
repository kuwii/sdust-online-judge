# -*- coding: utf-8 -*-
from json import loads, dumps

import redis
import time

from conf import queue, subscribe, local_queue, default_status
from conf import redis_db, local_redis_db

pool = redis.ConnectionPool(
    host=redis_db['host'],
    port=int(redis_db['port']),
    db=int(redis_db['db']),
    password=redis_db['password']
)
r = redis.Redis(connection_pool=pool)

local_pool = redis.ConnectionPool(
    host=local_redis_db['host'],
    port=int(local_redis_db['port']),
    db=int(local_redis_db['db']),
    password=local_redis_db['password']
)
lr = redis.Redis(connection_pool=local_pool)

sub_analyse_key = local_queue['submission-analyse']


class TestData(object):
    @staticmethod
    def write(problem_id, test_in, test_out):
        """
        将数据发送到HUSTOJ本地的写入器，写入测试数据。
        :param problem_id: HUSTOJ题目的ID。
        :param test_in: bytes类型，测试输入。
        :param test_out: bytes类型，测试输出。
        :return: 无返回值。
        """
        if test_in is None:
            test_in = b''
        if test_out is None:
            test_out = b''
        test_data = {
            'problem_id': str(problem_id),
            'test_in': test_in.decode('utf-8'),
            'test_out': test_out.decode('utf-8')
        }
        lr.rpush(local_queue['test-data'], dumps(test_data))


class SpecialJudge(object):
    @staticmethod
    def write(problem_id, code):
        """
        将数据发送到HUSTOJ本地的写入器，写入特殊评测数据。
        :param problem_id: HUSTOJ题目的ID。
        :param code: 特殊评测代码。
        :return: 无返回值。
        """
        special_judge = {
            'problem_id': str(problem_id),
            'code': code.decode('utf-8')
        }
        lr.rpush(local_queue['special-judge'], dumps(special_judge))


class Submission(object):

    @staticmethod
    def _get_key(submission_id):
        return str(submission_id)

    @staticmethod
    def mark(submission_id, submission_info):
        """
        标记提交，之后分析器将持续追踪此提交的动态直至评测完成。
        :param submission_id: SDUSTOJ提交的ID。
        :param submission_info: 列表，SDUSTOJ提交对应的HUSTOJ提交信息。
        :return: 无返回值。
        """
        key = Submission._get_key(submission_id)
        for test_id, solution_id in submission_info:
            lr.hset(key, test_id, solution_id)
        lr.rpush(sub_analyse_key, key)

    @staticmethod
    def unmark(submission_id):
        """
        删除提交的标记，之后分析器将不再追踪此提交。
        :param submission_id: SDUSTOJ提交的ID。
        :return: 无返回值。
        """
        key = Submission._get_key(submission_id)
        if lr.exists(key):
            lr.delete(key)

    @staticmethod
    def remove_status(submission_id, test_data_id):
        """
        从标记的一条提交的标记信息中删除某条测试数据的评测信息。
        :param submission_id: SDUSTOJ提交的ID。
        :param test_data_id: SDUSTOJ测试数据ID。
        :return: 无返回值。
        """
        key = Submission._get_key(submission_id)
        lr.hdel(key, test_data_id)

    @staticmethod
    def get_status(submission_id):
        """
        获取被标记提交的状态信息。
        :param submission_id: SDUSTOJ提交的ID。
        :return: 若提交被标记，返回含有状态信息的字典，键为测试数据ID，值为HUSTOJ提交ID，否则返回None。
        """
        key = Submission._get_key(submission_id)
        if lr.exists(key):
            ret = dict()
            for k, v in lr.hgetall(key).items():
                ret[int(k.decode('utf-8'))] = int(v.decode('utf-8'))
            return ret
        else:
            return None

    @staticmethod
    def push(submission_id):
        """
        将标记提交放回分析队列，继续下一轮分析。
        :param submission_id:  SDUSTOJ提交的ID。
        :return: 无返回值。
        """
        lr.rpush(sub_analyse_key, submission_id)

    @staticmethod
    def analyse_mark_submissions(handler):
        """
        分析处理标记的提交。
        :param handler: 处理函数。
        :return: 无返回值。
        """
        while True:
            info = lr.blpop(sub_analyse_key, timeout=1)
            if info is not None:
                sid = int(info[1].decode('utf-8'))
                handler(sid)
            time.sleep(0.5)


def get_command(handler):
    while True:
        info = r.blpop(queue, timeout=1)
        if info is not None:
            command = loads(info[1].decode('utf-8'))
            handler(command)


def get_queue_info(name):
    info = r.lpop(name)
    return info


def get_subscribe(handler):
    ps = r.pubsub()
    ps.subscribe(*subscribe)
    while True:
        message = ps.get_message(ignore_subscribe_messages=True)
        if message:
            handler(message)
        time.sleep(0.5)
