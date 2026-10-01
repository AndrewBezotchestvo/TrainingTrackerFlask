from flask import Flask, render_template, session, redirect, url_for, request, flash
from datetime import datetime, timedelta

from sqlalchemy.testing.pickleable import User

from forms import LoginForm, RegisterForm, ExerciseForm
from models import Exercises, Users, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///training.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '324dsfdsfsdfvsd'
app.secret_key = "dsfcdsfvds324432"
app.permanent_session_lifetime = timedelta(minutes=120)

db.init_app(app)

def check_user_in_session():
    is_user = session.get('user_id')
    if is_user:
        return True
    else:
        return False

@app.route('/')
def index():
    if check_user_in_session():
        form = ExerciseForm()

        if form.validate_on_submit():
            title = form.title.data
            category = form.category.data
            value = form.value.data
            repeat = form.repeat.data
        return render_template('index.html', form=form)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = Users.query.filter_by(email=email, password=password).first()
        print(user)
        if user:
            session['user_id'] = Users.query.filter_by(email=email).first().id
            session.permanent = True
            return redirect('/')
        else:
            flash("Такой пользователя не существует", "error")

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        users = Users.query.filter_by(email=email).first()
        if users:
            flash("Такой пользователь уже существует", "error")
        else:
            user = Users(name=name, email=email, password=password)
            db.session.add(user)
            db.session.commit()

            session['user_id'] = Users.query.filter_by(email=email).first().id
            session.permanent = True

            return redirect('/')
    return render_template('register.html', form=form)

@app.route('/exercise/add', methods=['GET', 'POST'])
def exercise():
    return render_template('exercise.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

