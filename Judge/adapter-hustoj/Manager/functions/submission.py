from datetime import datetime

from models import pg_models, mysql_models
from sqlalchemy.orm import sessionmaker

from conf import language, user, try_max, judger, status as status_map, final_status, priority

from functions.problem import get_problem_title, update as update_problem

from models.redis_models import Submission

from .log import print_log

from conf import judger_id

PgSession = sessionmaker(bind=pg_models.engine)
pg_session = PgSession()

MysqlSession = sessionmaker(bind=mysql_models.engine)
mysql_session = MysqlSession()


def update(**kwargs):
    sid = int(kwargs['sid'])
    # 获得提交信息
    language_id = language[kwargs['language']]
    submission = pg_session.query(pg_models.Submission).filter_by(id=sid).first()
    code = pg_session.query(pg_models.SubmissionCode).filter_by(submission_id=sid).first().code['code']

    # 根据分拆的题目生成相应的HUSTOJ提交
    problem_test = pg_session.query(pg_models.ProblemTestData).filter_by(
        problem_id=submission.problem_id, deleted=False
    ).all()
    ok = False
    submission_create = []
    submission_mark = []
    tried = 0
    while ok is False:
        # 查询题目，生成提交
        ok = True
        submission_create.clear()
        submission_mark.clear()
        tried += 1
        for pt in problem_test:
            title = get_problem_title(pt.problem_id, pt.test_data_id)
            problem = mysql_session.query(mysql_models.Problem).filter_by(title=title).first()
            if problem is None:
                # 若未找到题目，可能是题目尚未更新，更新题目后重新生成
                update_problem(pid=pt.problem_id)
                ok = False
                break

            solution = mysql_models.Solution(
                problem_id=problem.problem_id,
                user_id=user['user_id'],
                language=language_id,
                ip=str(submission.ip),
                code_length=submission.length,
                judger=judger,
                in_date=submission.submit_time
            )

            submission_create.append(solution)
            submission_mark.append((pt.test_data_id, solution))

        if (not ok) and tried > try_max:
            # 若尝试一定次数后仍未找到题目，有可能此提交信息有问题，放弃生成
            break

    mysql_session.add_all(submission_create)
    mysql_session.commit()

    code_create = []
    code_user_create = []
    sub_mark = []
    for tid, sub in submission_mark:
        print_log('Submission Updated: %s' % (sub.solution_id,))
        # 向数据库中写入代码
        code_create.append(mysql_models.SourceCode(
            solution_id=sub.solution_id,
            source=code
        ))
        code_user_create.append(mysql_models.SourceCodeUser(
            solution_id=sub.solution_id,
            source=code
        ))
        # 标记提交
        sub_mark.append((tid, sub.solution_id))
    mysql_session.add_all(code_create)
    mysql_session.add_all(code_user_create)
    mysql_session.commit()
    Submission.mark(submission.id, sub_mark)


def _handler(sid):
    status = Submission.get_status(sid)
    if status is None:
        return

    print_log('Analysing submission %s' % (sid, ))

    test_status = pg_session.query(pg_models.TestDataStatus).filter_by(submission_id=sid).first()
    info = test_status.status

    finished = True
    max_time = -1
    max_memory = -1
    max_status = 4
    for test_data_id, solution_id in status.items():
        solution = mysql_session.query(mysql_models.Solution).filter_by(solution_id=solution_id).first()
        result = solution.result
        info[str(test_data_id)]['status'] = status_map[result]
        info[str(test_data_id)]['time'] = solution.time
        info[str(test_data_id)]['memory'] = solution.memory

        if solution.time > max_time:
            max_time = solution.time
        if solution.memory > max_memory:
            max_memory = solution.memory
        if priority[result] > priority[max_status]:
            max_status = result

        print('\tGot solution %s, result is %s' % (solution_id, result))

        if result in final_status:
            Submission.remove_status(sid, test_data_id)
            print('\t\tSolution is judged, removed from mark.')
        else:
            finished = False

    table = pg_models.TestDataStatus.__table__
    pg_session.execute(
        table.update().where(table.c.submission_id == sid), {'status': info}
    )
    pg_session.commit()

    submission = pg_session.query(pg_models.Submission).filter_by(id=sid).first()
    submission.judge_id = judger_id
    if not finished:
        Submission.push(sid)
        submission.status = status_map[max_status]
        print('\tNot finished, pushed.')
    else:
        submission.time = max_time
        submission.memory = max_memory
        submission.status = status_map[max_status]
        submission.finished = True
        print('\tFinished, unmarked.')
    pg_session.commit()
    print('\tSubmission %s updated.' % (sid, ))


def analyse():
    Submission.analyse_mark_submissions(_handler)
