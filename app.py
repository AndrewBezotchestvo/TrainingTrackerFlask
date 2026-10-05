
from flask import Flask, render_template, session, redirect, url_for, request, flash
from datetime import datetime, timedelta

from forms import LoginForm, RegisterForm, ExerciseForm
from models import Exercises, Users, db, ExerciseHistory

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

@app.route('/',  methods=['GET', 'POST'])
def index():
    if check_user_in_session():
        form = ExerciseForm()
        user_id = session.get('user_id')

        if request.method == 'POST':
            title = form.title.data
            category = form.category.data
            value = form.value.data
            repeat = form.repeat.data

            exercise = Exercises.query.filter_by(title=title, category=category, user_id=user_id).first()

            if exercise is not None:
                exercise_history = ExerciseHistory(exercise_id=exercise.id, value=exercise.value, repeat=exercise.repeat, date=exercise.date)
                exercise.value = value
                exercise.repeat = repeat
                exercise.date = datetime.now()
                db.session.add(exercise_history)
                db.session.commit()
            else:
                exercise = Exercises(user_id=user_id, title=title, category=category, value=value, repeat=repeat)
                db.session.add(exercise)
                db.session.commit()
            return redirect("/")

        exercises = Exercises.query.filter_by(user_id=user_id).all()
        return render_template('index.html', form=form, exercises=exercises)
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
            flash("Такой пользователя не существует", "success")

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

@app.route('/exercise/delete/<int:exercise_id>')
def delete_exercise(exercise_id):
    exercise = Exercises.query.get(exercise_id)
    db.session.delete(exercise)

    exercise_history = ExerciseHistory.query.filter_by(exercise_id=exercise_id).all()
    for history in exercise_history:
        db.session.delete(history)
    db.session.commit()

    return redirect("/")

@app.route('/exercise/history/<int:exercise_id>')
def show_exercise_history(exercise_id):
    exercise = Exercises.query.get(exercise_id)
    exercise_history = ExerciseHistory.query.filter_by(exercise_id=exercise_id).all()
    return render_template("exercise_history.html", exercise_history=exercise_history, exercise=exercise)

@app.route('/exercise-semple/delete/<int:exercise_history_id>')
def delete_exercise_semple(exercise_history_id):
    exercise_history = ExerciseHistory.query.get(exercise_history_id)
    exercise_id = exercise_history.exercise_id
    db.session.delete(exercise_history)
    db.session.commit()
    return redirect(f"/exercise/history/{exercise_id}")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

