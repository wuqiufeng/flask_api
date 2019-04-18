import os


class Config:
    # Mysql
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:ace123@111.231.87.209:3306/test"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 是否打印SQL
    PRINT_SQL = False

    # Redis
    REDIS_HOST = '111.231.87.209'
    REDIS_PORT = 6379
    REDIS_PASSWD = 'ace123'

    # app用户前缀
    APP_USER_PREFIX = 'app'
    # 网页用户前缀
    WEB_USER_PREFIX = 'web'

    # Token生成串
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or "38ea77df71614caeb001b3b1c1c608d7"
    # Token过期时间
    JWT_EXP_TIME = 14 * 24 * 60 * 60


class IntConfig(Config):
    pass


class DevConfig(Config):
    pass


config = {
    "development": DevConfig,
    "default": IntConfig,
}
