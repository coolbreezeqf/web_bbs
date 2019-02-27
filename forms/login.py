from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length


class LoginForm(Form):
    username = StringField('用户名', validators=[DataRequired(), Length(3, 16)])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登陆')


