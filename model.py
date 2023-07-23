from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
session = db.session

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    private = db.Column(db.Boolean, default=False)
    report = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Note_File(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    note = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)
    file_name = db.Column(db.String(20))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(20), nullable=False)

def add(obj):
    session.add(obj)
    session.commit()
    return obj.id

def delete(obj):
    session.delete(obj)
    session.commit()

def update_filename(file_id, file_name):
    Note_File.query.filter_by(id=file_id).update(dict(file_name=file_name))
    session.commit()

def dummy_data():
    user_1 = User(id=1, first_name='Israel', last_name='Israeli')
    user_2 = User(id=2, first_name='Sea', last_name='Light')
    report_1 = Report(id=1, title='MyReport_1')
    report_2 = Report(id=2, title='MyReport_2')
    note_1 = Note(title='First Note', description='description_1', private=True, report=report_1.id, created_by=user_1.id)
    note_2 = Note(title='Second Note', description='description_2', report=report_2.id, created_by=user_2.id)
    for x in (user_1, user_2, report_1, report_2, note_1, note_2):
        add(x)
