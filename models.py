from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(12), nullable=False)

class Exercises(db.Model):
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(64), nullable=False)
    category = db.Column(db.String(64), default="s")
    value = db.Column(db.Float, nullable=False)
    repeat = db.Column(db.Integer, nullable=True)
    date = db.Column(db.DateTime, default=datetime.now())

class ExerciseHistory(db.Model):
    __tablename__ = 'exercise_history'
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    repeat = db.Column(db.Integer, nullable=True)
    date = db.Column(db.DateTime, default=datetime.now())