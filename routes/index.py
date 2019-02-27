import os
import uuid

from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    make_response,
    abort,
    send_from_directory,
    flash
)
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from models.reply import Reply
from models.topic import Topic
from models.user import User
from routes import current_user

from forms.register import RegisterForm
from forms.login import LoginForm

import json
import redis

cache = redis.StrictRedis()

from utils import log

main = Blueprint('index', __name__)



@main.route("/")
def index():
    # u = current_user()
    # return render_template("index.html", user=u)
    return redirect(url_for('topic.index'))


@main.route("/register", methods=['GET', 'POST'])
def register():
    # form = request.form.to_dict()
    # # 用类函数来判断
    # u = User.register(form)
    # flash("注册" + ("成功" if u else "失败"))
    # return redirect(url_for('.login'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.register(form.data)
        if user:
            flash('注册成功')
        else:
            flash('注册失败')
        return redirect(url_for('.login'))
    return render_template("register.html", form=form)


@main.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.validate_login(form.data)
        if u is None:
            flash('username or password is wrong.')
            return render_template('login.html')
        else:
            # session 中写入 user_id
            session['user_id'] = u.id
            # 设置 cookie 有效期为 永久
            session.permanent = True
            # 转到 topic.index 页面
            return redirect(url_for('topic.index'))
    else:
        return render_template('login.html', form=form)

@main.route("/logout")
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    return redirect(url_for('.login'))


def created_topic(user_id):
    # O(n)
    # ts = Topic.all(user_id=user_id)
    # return ts

    k = 'created_topic_{}'.format(user_id)
    if cache.exists(k):
        v = cache.get(k)
        ts = json.loads(v)
        return ts
    else:
        ts = Topic.all(user_id=user_id)
        v = json.dumps([t.json() for t in ts])
        cache.set(k, v)
        return ts


def replied_topic(user_id):
    # O(k)+O(m*n)
    # rs = Reply.all(user_id=user_id)
    # ts = []
    # for r in rs:
    #     t = Topic.one(id=r.topic_id)
    #     ts.append(t)
    # return ts
    #
    k = 'replied_topic_{}'.format(user_id)
    if cache.exists(k):
        v = cache.get(k)
        ts = json.loads(v)
        return ts
    else:
        rs = Reply.all(user_id=user_id)
        ts = []
        for r in rs:
            t = Topic.one(id=r.topic_id)
            ts.append(t)

        v = json.dumps([t.json() for t in ts])
        cache.set(k, v)

        return ts


@main.route('/profile')
@main.route('/profile/<string:username>')
def profile(username=None):
    if username:
        u = User.one(username=username)
        if u is None:
            return abort(404)
    else:
        u = current_user()
        if u is None:
            return redirect(url_for('.login'))

    create_topic = Topic.all(user_id=u.id)
    create_topic = sorted(create_topic, key=lambda k: k.created_time, reverse=True)

    reply = Reply.all(user_id=u.id)
    reply_topic = []
    for r in reply[::-1]:
        topic = Topic.one(id=r.topic_id)
        reply_topic.append(topic)

    return render_template(
        'profile.html',
        user=u,
        created=create_topic,
        replied=reply_topic,
    )


@main.route('/setting')
def setting():
    u = current_user()
    if u is None:
        return redirect(url_for('.index'))
    else:
        return render_template('setting.html')


@main.route('/user/update/profile', methods=['POST'])
def update_profile():
    form = request.form.to_dict()
    user: User = current_user()
    User.update(user.id, **form)
    return redirect(url_for('.setting'))


@main.route('/user/update/password', methods=['POST'])
def update_password():
    form = request.form
    old_password = form['old_pass']
    new_password = form['new_pass']
    user = current_user()
    if user.validate_password(old_password):
        user.update_password(new_password)
        return redirect(url_for('.setting'))
    else:
        return "修改失败"


@main.route('/user/<int:id>')
def user_detail(id):
    u = User.one(id=id)
    if u is None:
        abort(404)
    else:
        return render_template('profile.html', user=u)


@main.route('/image/add', methods=['POST'])
def avatar_add():
    file: FileStorage = request.files['avatar']

    # filename = file.filename
    # ../../root/.ssh/authorized_keys
    # images/../../root/.ssh/authorized_keys
    # filename = secure_filename(file.filename)
    suffix = file.filename.split('.')[-1]
    filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
    path = os.path.join('images', filename)
    file.save(path)

    u = current_user()
    User.update(u.id, image='/images/{}'.format(filename))

    return redirect(url_for('.profile'))


@main.route('/images/<filename>')
def image(filename):
    # 不要直接拼接路由，不安全，比如
    # http://localhost:2000/images/..%5Capp.py
    # path = os.path.join('images', filename)
    # print('images path', path)
    # return open(path, 'rb').read()
    # if filename in os.listdir('images'):
    #     return
    return send_from_directory('images', filename)
