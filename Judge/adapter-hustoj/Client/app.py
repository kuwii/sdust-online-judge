# -*- coding: utf-8 -*-
import redis
import os
from json import loads

pool = redis.ConnectionPool(
    host='localhost', port=6379, db=0, password='hust'
)
r = redis.Redis(connection_pool=pool)


def make_dir(problem_id):
    path = '/home/judge/data/' + str(problem_id)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def write_test_data(redis_info):
    p_info = redis_info[1]
    data = loads(p_info.decode('utf-8'))
    problem_id = data['problem_id']
    test_in = data['test_in'].encode('utf-8')
    test_out = data['test_out'].encode('utf-8')
    path = make_dir(problem_id)
    i = open(path + '/test.in', 'wb')
    i.write(test_in)
    i.close()
    o = open(path + '/test.out', 'wb')
    o.write(test_out)
    o.close()
    print('[WriteTestData] problem %s' % (problem_id, ))


def write_special_judge(redis_info):
    p_info = redis_info[1]
    data = loads(p_info.decode('utf-8'))
    problem_id = data['problem_id']
    code = data['code'].encode('utf-8')
    path = make_dir(problem_id)
    c = open(path + '/spj.cc', 'wb')
    c.write(code)
    c.close()
    print('[WriteSpecialJudge] problem %s' % (problem_id,))
    os.system('g++ -o '+path+'/spj '+path+'/spj.cc')
    os.system('chmod +x '+path+'/spj')


func = {
    'test-data': write_test_data,
    'special-judge': write_special_judge
}


while True:
    info = r.blpop(('test-data', 'special-judge'), timeout=1)
    if info is not None:
        kwarg = info[0].decode('utf-8')
        func[kwarg](info)
