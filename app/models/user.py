from sqlalchemy import Column, Integer, String, SmallInteger, FetchedValue, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app.libs.enums import UserAdmin, UserActive
from app.libs.error_code import NotFound, AuthFailed
from app.models.base import InfoCrud, BaseCrud


class User(InfoCrud):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String(32), unique=True)
    # : admin express the user is admin(admin) ;  1 -> common |  2 -> admin
    # : admin 代表是否为超级管理员 ;  1 -> 普通用户 |  2 -> 超级管理员
    admin = Column(SmallInteger, nullable=False, default=1, server_default=FetchedValue(),
                   comment="是否为超级管理员 ;  1 -> 普通用户 |  2 -> 超级管理员")
    # : active express the user can manage the authorities or not ; 1 -> active | 2 -> not
    # : active 代表当前用户是否为激活状态，    active = Column(SmallInteger, nullable=False, default=1, server_default=FetchedValue(),非激活状态默认失去用户权限 ; 1 -> 激活 | 2 -> 非激活
    active = Column(SmallInteger, nullable=False, default=1, server_default=FetchedValue(),
                    comment="当前用户是否为激活状态，非激活状态默认失去用户权限 ; 1 -> 激活 | 2 -> 非激活")

    # : which group the user belongs,nullable is true
    # : 用户所属的权限组id
    group_id = Column(Integer)
    _password = Column('password', String(100))

    # avatar_url = Column(String(128), comment='头像')
    # email = Column(String(100), unique=True, comment="电子邮箱")
    # phone = Column(String(11), unique=True)
    # uuid = db.Column(db.String(255), unique=True)  # 唯一标识符

    user_auth = relationship('UserAuth', backref="users", lazy='dynamic')

    def __repr__(self):
        return '<Users:{}>'.format(self.nickname)

    def _set_fields(self):
        self._exclude = ['password']

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    @property
    def is_admin(self):
        return self.admin == UserAdmin.ADMIN.value

    @property
    def is_active(self):
        return self.active == UserActive.ACTIVE.value

    @classmethod
    def verify(cls, nickname, password):
        raise Exception('must implement this method')

    def check_password(self, raw):
        if not self._password:
            return False
        return check_password_hash(self._password, raw)

    def reset_password(self, new_password):
        raise Exception('must implement this method')

    def change_password(self, old_password, new_password):
        raise Exception('must implement this method')

    @classmethod
    def find_user(cls, nickname):
        return cls.query.filter_by(nickname=nickname).first()

    @classmethod
    def verify(cls, nickname, password):
        user = cls.query.filter_by(nickname=nickname).first()
        if user is None:
            raise NotFound(msg='用户不存在')
        if not user.check_password(password):
            raise AuthFailed(msg='密码错误，请输入正确密码')
        return user





class AuthInterface(BaseCrud):
    __tablename__ = 'user_auth'

    id = Column(Integer, primary_key=True)
    # : belongs to which group
    # : 所属权限组id
    group_id = Column(Integer, nullable=False, comment="所属权限组id")
    # : authority field
    # : 权限字段
    auth = Column(String(60), comment="权限字段")
    # : authority module, default common , which can sort authorities
    # : 权限的模块
    module = Column(String(50), comment="权限的模块")


class GroupInterface(BaseCrud):
    __tablename__ = 'lin_group'

    id = Column(Integer, primary_key=True)
    # : name of group
    # : 权限组名称
    name = Column(String(60), comment="权限组名称")
    # a description of a group
    # 权限组描述
    info = Column(String(255), comment="权限组描述")


"""
class UserAuth(BaseCrud):
    __tablename__ = 'user_auth'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    # 登录类型(手机号 邮箱 用户名)或第三方应用名称(微信 微博)
    identity_type = Column(String(64), comment='登陆方式')
    # 标识（手机号 邮箱 用户名或第三方应用的唯一标识）
    identifier = Column(String(64), comment='账号标识')
    # 密码凭证（站内的保存密码，站外的不保存或保存token）
    credential = Column(String(128), comment='凭证')

    def __repr__(self):
        return '<UserAuth: {},{},{},{},{}>'.format(
            self.id,
            self.user_id,
            self.identity_type,
            self.identifier,
            self.credential
        )
"""