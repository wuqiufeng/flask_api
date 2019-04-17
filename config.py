


class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:ace123@111.231.87.209:3306/test"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 是否打印SQL
    PRINT_SQL = False


class IntConfig(Config):
    pass

class DevConfig(Config):
    pass




config = {
    "development": DevConfig,
    "default": IntConfig,
}