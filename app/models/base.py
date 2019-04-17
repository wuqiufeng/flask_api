from datetime import datetime
from sqlalchemy import Column, TIMESTAMP

from app.models import db, MixinJSONSerializer
from app.utils.str_util import camel2line


class BaseCrud(db.Model, MixinJSONSerializer):
    __abstract__ = True

    def __init__(self):
        name: str = self.__class__.__name__
        if not hasattr(self, '__tablename__'):
            self.__tablename__ = camel2line(name)

    def _set_fields(self):
        self._exclude = []

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    # 硬删除
    def delete(self, commit=False):
        db.session.delete(self)
        if commit:
            db.session.commit()

    # 查
    @classmethod
    def get(cls, start=None, count=None, one=True, **kwargs):
        if one:
            return cls.query.filter().filter_by(**kwargs).first()
        return cls.query.filter().filter_by(**kwargs).offset(start).limit(count).all()

    # 增
    @classmethod
    def create(cls, **kwargs):
        one = cls()
        for key in kwargs.keys():
            if hasattr(one, key):
                setattr(one, key, kwargs[key])
        db.session.add(one)
        if kwargs.get('commit') is True:
            db.session.commit()
        return one

    def update(self, **kwargs):
        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        db.session.add(self)
        if kwargs.get('commit') is True:
            db.session.commit()
        return self


# 提供软删除，及创建时间，更新时间信息的crud model
class InfoCrud(db.Model, MixinJSONSerializer):
    __abstract__ = True
    _create_time = Column('create_time', TIMESTAMP(True), default=datetime.now)
    update_time = Column(TIMESTAMP(True), default=datetime.now, onupdate=datetime.now)
    delete_time = Column(TIMESTAMP(True))

    def __init__(self):
        name: str = self.__class__.__name__
        if not hasattr(self, '__tablename__'):
            self.__tablename__ = camel2line(name)

    def _set_fields(self):
        self._exclude = ['update_time', 'delete_time']

    @property
    def create_time(self):
        if self._create_time is None:
            return None
        return int(round(self._create_time.timestamp() * 1000))

    # @property
    # def update_time(self):
    #     if self._update_time is None:
    #         return None
    #     return int(round(self._update_time.timestamp() * 1000))

    # @property
    # def delete_time(self):
    #     if self._delete_time is None:
    #         return None
    #     return int(round(self._delete_time.timestamp() * 1000))

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    # 软删除
    def delete(self, commit=False):
        self.delete_time = datetime.now()
        db.session.add(self)
        # 记得提交会话
        if commit:
            db.session.commit()

    # 硬删除
    def hard_delete(self, commit=False):
        db.session.delete(self)
        if commit:
            db.session.commit()

    # 查
    @classmethod
    def get(cls, start=None, count=None, one=True, **kwargs):
        # 应用软删除，必须带有delete_time
        if kwargs.get('delete_time') is None:
            kwargs['delete_time'] = None
        if one:
            return cls.query.filter().filter_by(**kwargs).first()
        return cls.query.filter().filter_by(**kwargs).offset(start).limit(count).all()

    # 增
    @classmethod
    def create(cls, **kwargs):
        one = cls()
        for key in kwargs.keys():
            # if key == 'from':
            #     setattr(one, '_from', kwargs[key])
            # if key == 'parts':
            #     setattr(one, '_parts', kwargs[key])
            if hasattr(one, key):
                setattr(one, key, kwargs[key])
        db.session.add(one)
        if kwargs.get('commit') is True:
            db.session.commit()
        return one

    def update(self, **kwargs):
        for key in kwargs.keys():
            # if key == 'from':
            #     setattr(self, '_from', kwargs[key])
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        db.session.add(self)
        if kwargs.get('commit') is True:
            db.session.commit()
        return self