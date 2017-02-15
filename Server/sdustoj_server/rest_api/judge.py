import redis
from json import dumps
from .models import Judge
from config import REDIS_SETTINGS

pool = redis.ConnectionPool(
    host=REDIS_SETTINGS['host'], port=int(REDIS_SETTINGS['port']), db=0, password=REDIS_SETTINGS['password']
)
r = redis.Redis(connection_pool=pool)


# -- 更新题元及题目相关 ------------------------------------------------------------------------------------------------

def inform_machine(machine, info):
    r.rpush(machine, info)


def update_problem(problem):
    flag = set()
    for judge in problem.judge.all():
        if judge.id not in flag:
            flag.add(judge.id)
            inform_machine(judge.cmd_queue, dumps({
                'cmd': 'update',
                'type': 'problem',
                'pid': problem.id
            }))


def update_meta(meta_problem):
    for judge in Judge.objects.all():
        inform_machine(judge.cmd_queue, dumps({
            'cmd': 'update',
            'type': 'meta',
            'mid': meta_problem.id
        }))


def update_all():
    for judge in Judge.objects.all():
        inform_machine(judge.cmd_queue, dumps({
            'cmd': 'update',
            'type': 'all'
        }))


# -- 发布提交相关 ------------------------------------------------------------------------------------------------------


def push_submission(submission_id):
    r.rpush(str(submission_id), '')


def publish_submission(submission):
    judge_id = submission.environment.judge_id
    push_submission(submission.id)
    r.publish(judge_id, str(submission.id))
