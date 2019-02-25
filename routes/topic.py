from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.topic import Topic
from models.board import Board

main = Blueprint('topic', __name__)


@main.route("/")
def index():
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:
        ms = Topic.all()
    else:
        ms = Topic.all(board_id=board_id)
    bs = Board.all()
    return render_template("topic/index.html", ms=ms[::-1], bs=bs, bid=board_id)


@main.route('/<int:id>')
def detail(id):
    m: Topic = Topic.get(id)
    # 传递 topic 的所有 reply 到 页面中
    board = Board.one(id=m.board_id)
    return render_template("topic/detail.html", topic=m, board=board)


@main.route("/delete")
@csrf_required
def delete():
    id = int(request.args.get('id'))
    u = current_user()
    # print('删除 topic 用户是', u, id)
    Topic.get(id).delete()
    return redirect(url_for('.index'))


@main.route("/new")
@login_required
def new():
    board_id = int(request.args.get('board_id', 0))
    bs = Board.all()
    # return render_template("topic/new.html", bs=bs, bid=board_id)
    token = new_csrf_token()
    return render_template("topic/new.html", bs=bs, token=token, bid=board_id)


@main.route("/add", methods=["POST"])
@csrf_required
def add():
    form = request.form.to_dict()
    u = current_user()
    Topic.new(form, user_id=u.id)
    return redirect(url_for('.index'))
