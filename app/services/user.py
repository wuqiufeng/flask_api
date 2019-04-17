from app import db
from app.libs.error_code import RepeatException
from app.models.user import User
from app.services import BaseService


class UserService(BaseService):

    def post_user(self, form):
        nickname = form['nickname']
        user = User.find_user(nickname=nickname)
        if user:
            raise RepeatException(msg='用户名重复，请重新输入')
        self._register_user(form)

    @staticmethod
    def _register_user(form):
        with db.auto_commit():
            user = User()
            user.nickname = form['nickname']
            user.password = form['password']
            db.session.add(user)