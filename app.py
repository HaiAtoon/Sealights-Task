import os
from zipfile import ZipFile
from flask import Flask, request, send_from_directory
from model import db, Note, Note_File, add, update_filename, dummy_data

NOT_ALLOWED_EXTENSIONS = {'exe', 'js', 'vbs'}
UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
test_client = app.test_client()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1000 * 1000  # 10MB limit


@app.route("/save_note", methods=['POST'])
def save_note():
    data = request.json
    try:
        title = data["title"]
        description = data["description"]
        is_private = data.get("is_private", False)  # optional
        report = data["report"]
        created_by = data["created_by"]
        note = Note(
            title=title,
            description=description,
            private=is_private,
            report=report,
            created_by=created_by
        )
        note_id = add(note)
        return dict(status="success", data=f"Note added successfully (id = {note_id})")

    except Exception as e:
        return dict(status="failed", data=f"Couldn't add note = {str(e)}"), 400


@app.route("/get_report_notes", methods=['GET'])
def get_notes():
    report = request.args.get('report')
    if not report:
        return dict(status="failed", data="No report parameter received"), 400
    notes = Note.query.filter(Note.report == report).all()
    response = [
        {
            "note_id": note.id,
            "title": note.title
        }
        for note in notes
    ]
    return dict(status='success', data=response)


@app.route("/download_file", methods=['GET'])
def download_file():
    note = request.args.get('note_id')
    if not note:
        return dict(status="failed", data="No note parameter received"), 400
    files = Note_File.query.filter_by(note=note).all()
    with ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], 'download.zip'), 'w') as zip_obj:
        for file in files:
            zip_obj.write(os.path.join(app.config['UPLOAD_FOLDER'], file.file_name))
    return send_from_directory(directory='./uploads', path='download.zip')


@app.route("/upload_file", methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return dict(status='failed', data='No file part')
    file = request.files['file']
    note = request.form.get('note_id')
    if file.filename == '':
        return dict(status='failed', data='No selected file'), 400
    if not (note and Note.query.get(note)):
        return dict(status='failed', data='note_id wasn`t sent or incorrect'), 400
    if file and allowed_file(file.filename):
        file_id = str(add(Note_File(note=note)))
        file_name = file_id + '.' + file.filename.rsplit('.', 1)[1].lower()
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
        update_filename(file_id, file_name)
        return dict(status='success', data=f'The file was successfully uploaded and attached to note no. {note}')
    return dict(status="failed", data="general error"), 400


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() not in NOT_ALLOWED_EXTENSIONS


if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()
        dummy_data()
    app.run()