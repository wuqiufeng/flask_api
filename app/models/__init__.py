import json
import datetime
import redis
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
from sqlalchemy import inspect, orm, func, create_engine, event
from contextlib import contextmanager
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.orm import sessionmaker

from app.libs.error_code import NotFound
from config import config


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        # finally:
        #     self.session.close()


class Query(BaseQuery):

    def filter_by(self, soft=True, **kwargs):
        # soft 应用软删除
        soft = kwargs.get('soft')
        if soft:
            kwargs['delete_time'] = None
        if soft is not None:
            kwargs.pop('soft')
        return super(Query, self).filter_by(**kwargs)

    def get_or_404(self, ident):
        rv = self.get(ident)
        if not rv:
            raise NotFound()
        return rv

    def first_or_404(self):
        rv = self.first()
        if not rv:
            raise NotFound()
        return rv


db = SQLAlchemy(query_class=Query)


def get_total_nums(cls, is_soft=False, **kwargs):
    nums = db.session.query(func.count(cls.id))
    nums = nums.filter(cls.delete_time == None).filter_by(**kwargs).scalar() if is_soft else nums.filter().scalar()
    if nums:
        return nums
    else:
        return 0


class MixinJSONSerializer:
    @orm.reconstructor
    def init_on_load(self):
        self._fields = []
        self._exclude = []

        self._set_fields()
        self.__prune_fields()

    def _set_fields(self):
        pass

    def __prune_fields(self):
        columns = inspect(self.__class__).columns
        if not self._fields:
            all_columns = set([column.name for column in columns])
            self._fields = list(all_columns - set(self._exclude))

    def hide(self, *args):
        for key in args:
            self._fields.remove(key)
        return self

    def keys(self):
        return self._fields

    def __getitem__(self, key):
        return getattr(self, key)





SETTINGS = config["default"]
redis_pool = redis.ConnectionPool(host=SETTINGS.REDIS_HOST, port=SETTINGS.REDIS_PORT, db=0, password=SETTINGS.REDIS_PASSWD, encoding='utf-8', decode_responses=True)
redis_client = redis.Redis(connection_pool=redis_pool)

class CommonJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        return json.JSONEncoder.default(self, o)


def checkout_listener(dbapi_con, con_record, con_proxy):
    try:
        try:
            dbapi_con.ping(False)
        except TypeError:
            dbapi_con.ping()
    except dbapi_con.OperationalError as exc:
        if exc.args[0] in (2006, 2013, 2014, 2045, 2055):
            raise DisconnectionError()
        else:
            raise


def session_factory(db_uri=config['default'].SQLALCHEMY_DATABASE_URI):
    engine = create_engine(db_uri, echo=config["default"].PRINT_SQL,pool_size = 100, pool_recycle=3600)
    event.listen(engine, 'checkout', checkout_listener)
    return sessionmaker(bind=engine)


Session = session_factory()

@contextmanager
def action_session():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


@contextmanager
def query_session():
    session = Session()
    try:
        yield session
    except Exception as e:
        raise e
    finally:
        session.close()

