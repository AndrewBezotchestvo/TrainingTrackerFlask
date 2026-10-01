from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange, Length, ValidationError, Email, Optional
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, EmailField, PasswordField, SelectField, FloatField


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(6, 12)])
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(1, 64)])
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(6, 12)])
    submit = SubmitField('Войти')

class ExerciseForm(FlaskForm):
    title = StringField("Упражнение", validators=[DataRequired(), Length(1, 64)])
    category = SelectField("Тип", choices=[("s", "Силовая"),  ("с", "Кардио")])
    value = FloatField("Вес (кг)/ Дистанция (км)", validators=[DataRequired(), NumberRange(min=0, max=1000)])
    repeat = IntegerField("Повторения (для силовых)", validators=[Optional(), NumberRange(min=1, max=1000)])
    submit = SubmitField('Сохранение')
