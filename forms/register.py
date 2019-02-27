from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp
from models.user import User
from wtforms import ValidationError


class RegisterForm(Form):
    username = StringField('用户名', validators=[
        DataRequired(), Length(3, 16), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Username must have only letters, numbers, dots or underscores')])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message="密码必须相同")])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.one(username=field.data):
            raise ValidationError('用户名已被使用')
