from app import db, jwt
from app.libs.error_code import RepeatException
from app.models import redis_client
from app.models.user import User
from app.services import BaseService
from config import Config


class UserService(BaseService):

    def post_user(self, form):
        nickname = form['nickname']
        user = User.find_user(nickname=nickname)
        if user:
            raise RepeatException(msg='用户名重复，请重新输入')
        self._register_user(form)

    def login(self, form):
        nickname = form.pop('nickname')
        password = form.pop('password')
        user = User.verify(nickname=nickname, password=password)
        token = self._get_token(user)
        return token


    @staticmethod
    def _register_user(form):
        with db.auto_commit():
            user = User()
            user.nickname = form['nickname']
            user.password = form['password']
            db.session.add(user)

    @staticmethod
    def _get_token(user):
        jwt_id = '{}:{}'.format(user.id, user.nickname)
        token = jwt.dumps(jwt_id).decode()
        redis_client.set('token:{}'.format(jwt_id), token, ex=Config.JWT_EXP_TIME)
        return token