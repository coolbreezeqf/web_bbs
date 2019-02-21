from faker import Faker
from random import randint

from sqlalchemy import create_engine

from app import configured_app
from models.base_model import db
from models.board import Board
from models.reply import Reply
from models.topic import Topic
from models.user import User

import secret


def reset_database():
    uri = 'mysql+pymysql://root:{}@127.0.0.1/?charset=utf8mb4'.format(secret.database_password)
    e = create_engine(uri, echo=True)

    with e.connect() as c:
        c.execute('DROP DATABASE IF EXISTS web21')
        c.execute('CREATE DATABASE web21 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        c.execute('USE web21')

    db.metadata.create_all(bind=e)


def generate_fake_data():
    # cn_fake = Faker(locale='zh_CN')
    fake = Faker()
    form = dict(
        username='test',
        password='test',
    )
    test_user = User.register(form)
    if not test_user:
        print('test user create fail')

    form = dict(
        title='all'
    )
    b = Board.new(form)

    for i in range(50):
        form = dict(
            username=fake.name(),
            password=fake.password()
        )
        User.register(form)

    for i in range(100):
        print('fake data:', i)
        topic_form = dict(
            title=fake.sentence(nb_words=randint(4, 6)),
            board_id=b.id,
            content=fake.text(max_nb_chars=400),
            views=randint(10, 100),
        )
        t = Topic.new(topic_form, randint(1, 51))

        for j in range(randint(4, 10)):
            reply_form = dict(
                content=fake.text(max_nb_chars=200),
                topic_id=t.id,
            )
            Reply.new(reply_form, randint(1, 51))

    with open('static/doc/markdown_demo.md', encoding='utf8') as f:
        content = f.read()
        b = Board.new(dict(title='demo'))
        topic_form = dict(
            title='markdown 示例',
            board_id=b.id,
            content=content,
            views=randint(10, 100),
        )
        t = Topic.new(topic_form, randint(1, 51))
        reply_form = dict(
            content=content,
            topic_id=t.id,
        )
        Reply.new(reply_form, randint(1, 51))


if __name__ == '__main__':
    app = configured_app()
    with app.app_context():
        reset_database()
        generate_fake_data()
