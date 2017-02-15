from datetime import datetime

from models import mysql_models
from models import pg_models
from models.redis_models import get_command
from sqlalchemy.orm import sessionmaker

from functions import problem

MysqlSession = sessionmaker(bind=mysql_models.engine)
mysql_session = MysqlSession()

PgSession = sessionmaker(bind=pg_models.engine)
pg_session = PgSession()


class Function(object):
    @staticmethod
    def func(cmd):
        pass


class Update(Function):
    update_func = {
        'all': problem.update_all,
        'meta': problem.update_meta,
        'problem': problem.update
    }

    @staticmethod
    def func(cmd):
        Update.update_func[cmd['type']](**cmd)


func_classes = {
    'update': Update
}


def handler(command):
    print('[' + str(datetime.now()) + ']' + 'Get Command: ' + str(command))
    func_class = func_classes[command['cmd']]
    func_class.func(command)


get_command(handler)
