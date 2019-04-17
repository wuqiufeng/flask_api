
>swagger_py_codegen --swagger-doc ./app/swagger/api.yaml app -p . --ui --spec

##### 创建microblog的迁移存储库：
flask db init
#### 自动迁移, 生成迁移脚本
flask db migrate -m "users table"
#### 创建数据库
flask db upgrade
#### 回滚上次的迁移
flask db downgrade

