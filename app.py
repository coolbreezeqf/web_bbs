from flask import Flask
from flask_moment import Moment
from datetime import datetime

import secret
import config
from models.base_model import db
from models.store import redis_store

from routes import current_user
from routes.index import main as index_routes
from routes.topic import main as topic_routes
from routes.reply import main as reply_routes
from routes.board import main as board_routes
from routes.message import main as mail_routes, mail


def configured_app():
    # web framework
    # web application
    # __main__
    app = Flask(__name__)
    # 设置 secret_key 来使用 flask 自带的 session
    # 这个字符串随便你设置什么内容都可以
    app.secret_key = secret.secret_key

    # 现在 mysql root 默认用 socket 来验证而不是密码
    uri = 'mysql+pymysql://root:{}@127.0.0.1/web21?charset=utf8mb4'.format(secret.database_password)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    app.config['MAIL_SERVER'] = 'smtp.exmail.qq.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = config.admin_mail
    app.config['MAIL_PASSWORD'] = secret.mail_password

    mail.init_app(app)
    redis_store.init_app(app)
    moment = Moment(app)

    register_template_func(app)
    register_routes(app)
    return app


def register_template_func(app):
    app.template_global()(current_user)
    app.template_global()(datetime)


def register_routes(app):
    """
    注册蓝图
    """
    app.register_blueprint(index_routes)
    app.register_blueprint(topic_routes, url_prefix='/topic')
    app.register_blueprint(reply_routes, url_prefix='/reply')
    app.register_blueprint(board_routes, url_prefix='/board')
    app.register_blueprint(mail_routes, url_prefix='/mail')


# 运行代码
if __name__ == '__main__':
    app = configured_app()
    # 自动 reload jinja
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    config = dict(
        debug=True,
        host='localhost',
        port=2000,
        threaded=True,
    )
    app.run(**config)
