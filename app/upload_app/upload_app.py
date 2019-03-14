#!/usr/bin/env python
import json
import datetime
import couchdbkit
from couchdbkit import Document, StringProperty, DateTimeProperty
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Markup, jsonify, send_from_directory, make_response
from flask_bcrypt import Bcrypt
import logging
import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from wtforms import Form, BooleanField, StringField, PasswordField, SelectField, validators
import uuid
from celery import Celery
import subprocess32
from shutil import copy2, rmtree, make_archive
import glob
from timeit import timeit
from itertools import izip


DATABASE = 'upload_app'
DEBUG = True
SECRET_KEY = 'development key'
CELERY_BROKER_URL = 'redis://redis-node:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis-node:6379/0'
if "COUCHDB_USER" and "COUCHDB_PASS" in os.environ:
    COUCHDB_URL = 'http://%s:%s@couchdb-node:5984' % (os.getenv("COUCHDB_USER"), os.getenv("COUCHDB_PASS"))
else:
    COUCHDB_URL = 'http://admin:admin@couchdb-node:5984'

UPLOAD_FOLDER = 'static/uploads'
SEND_FILE_MAX_AGE_DEFAULT = 0
SOURCE_FOLDER = 'run/src'
BUILD_FOLDER = 'run/build'
PROBLEMS = ['diamonds', 'verbal_tics', 'text_tree']
LANGUAGES = {
    'c': ['C', "gcc -Wall -static -O2 -I. file.c"],
    'cpp': ['C++', "g++ -std=c++11 -Wall -static -O2 -I. file.cpp"],
    'java': ['Java', "javac Main.java"],
    'py': ['Python', "python file.py"]
}
ALLOWED_EXTENSIONS = set(['cc', 'c', 'h', 'cpp', 'pas', 'java', 'py', 'c++', 'hh', 'hpp', 'h++'])

basedir = os.path.abspath(os.path.dirname(__file__))
home = os.path.expanduser('~')
working_directory = home + '/celery/'

app = Flask(__name__)
app.config.from_object(__name__)
Bootstrap(app)
bcrypt = Bcrypt(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (getattr(form, field).label.text, error), 'danger')


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


def connect_db():
    server = couchdbkit.Server(app.config['COUCHDB_URL'])
    return server.get_or_create_db(app.config['DATABASE'])


def init_db():
    db = connect_db()
    loader = couchdbkit.loaders.FileSystemDocsLoader('_design')
    loader.sync(db, verbose=True)


class User(Document):
    username = StringProperty()
    email = StringProperty()
    password = StringProperty()
    date = DateTimeProperty()


class Entry(Document):
    author = StringProperty()
    email = StringProperty()
    date = DateTimeProperty()


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=50)])
    email = StringField('Email Address', [validators.Email()])
    password = PasswordField('Password', [
        validators.Length(min=4),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    grade = SelectField('Grade', [validators.DataRequired()], choices=[('elev', 'elev'), ('student', 'student')])


@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db()
    Entry.set_db(g.db)
    User.set_db(g.db)


@app.teardown_request
def teardown_request(exception):
    """Closes the database at the end of the request."""



openContest  = "2018-11-23 10:00:00"
closeRanking = "2018-11-23 12:30:00"
closeContest = "2018-11-23 14:00:00"

def isAfterContest():
    timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    return (timestamp > closeContest)

def isBeforeContest():
    timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    return (timestamp < openContest)

def isRankingClosed():
    timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    return (timestamp > closeRanking)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if isBeforeContest():
        return render_template('placeholder_before.html', countDownTo=openContest)
    if isAfterContest():
        return render_template('placeholder_after.html')

    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        check_user = g.db.view("users/by_username", key=request.form['username'])
        check_email = g.db.view("users/by_email", key=request.form['email'])
        if check_user.first():
            flash("An user with this name already exists.", 'danger')
            return redirect(url_for('register'))
        if check_email.first():
            flash(Markup("An user with this email already exists. <a href='/login'>Login</a> if you already have an account."), 'danger')
            return redirect(url_for('register'))
        user = User(username=request.form['username'], email=request.form['email'],
                    password=bcrypt.generate_password_hash(request.form['password']),
                    grade=request.form['grade'], date=datetime.datetime.utcnow())
        g.db.save_doc(user)
        flash(Markup('Thanks for registering! You can now <a href="/login">login</a>.'), 'success')
        return redirect(url_for('status'))
    else:
        flash_errors(form)
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if isBeforeContest():
        return render_template('placeholder_before.html', countDownTo=openContest)
    if isAfterContest():
        return render_template('placeholder_after.html')
    error = None
    if request.method == 'POST':
        result = g.db.view("users/by_email", key=request.form['email'])
        if result.first() is None:
            error = 'Invalid email'
        else:
            user = result.first()
            if not bcrypt.check_password_hash(user['value'][0], request.form['password']):
                error = 'Invalid credentials'
            else:
                session['logged_in'] = True
                session['email'] = request.form['email']
                session['username'] = user['value'][3]
                session['grade'] = user['value'][1]
                if user['value'][2]:
                    session['admin'] = user['value'][2]
                flash('You were successfully logged in', 'success')
                # print url_for('status')
                # print redirect(url_for('status')).get_data()
                # print redirect(url_for('status')).headers
                return redirect(url_for('status'))
    return render_template('login.html', error=error)


@app.route('/static/uploads/<path:path>')
def uploads(path):
    if isBeforeContest():
        return render_template('placeholder_before.html', countDownTo=openContest)
    if isAfterContest():
        return render_template('placeholder_after.html')
    if session.get('logged_in'):
        files = g.db.view("users/by_uploads", key=session.get('username'))
        if files.first() or session.get('is_admin'):
            for file in files:
                if path in file['id']:
                    path = path + '.' + file['value'][2]
                    return send_from_directory(os.path.join('.', 'static', 'uploads'), path, as_attachment=True, attachment_filename=file['value'][0])
    flash("You are not authorized to view this file", 'danger')
    return redirect(url_for('status'))


@app.route('/')
def status():
    if isBeforeContest():
        return render_template('placeholder_before.html', countDownTo=openContest)
    if isAfterContest():
        return render_template('placeholder_after.html')
    files = None
    if session.get('logged_in'):
        if session.get('admin'):
            files = g.db.view("users/by_uploads")
        else:
            files = g.db.view("users/by_uploads", key=session.get('username'))
    return render_template('status.html', files=files, problems=app.config['PROBLEMS'], languages=app.config['LANGUAGES'])


@app.route('/add', methods=['POST'])
def add_entry():
    if isBeforeContest():
        return render_template('placeholder_before.html', countDownTo=openContest)
    if isAfterContest():
        return render_template('placeholder_after.html')
    if not session.get('logged_in'):
        abort(401)
    if 'file-source' not in request.files:
        flash('Missing source file', 'danger')
        return redirect(url_for('status'))
    if request.files['file-source'].filename == '':
        flash('Missing source file', 'danger')
        return redirect(url_for('status'))
    existing = g.db.view("users/by_existing", key=[session.get('username'), request.form['problem']])
    if existing.first():
        flash('You can only upload one of each problem at a time', 'danger')
        return redirect(url_for('status'))
    sourcefile = request.files['file-source']
    if sourcefile and allowed_file(sourcefile.filename):
        unique_id = str(uuid.uuid4())
        sourcefilename = secure_filename(sourcefile.filename)
        if request.form['language'] == 'c':
            sourceSavedFilename = unique_id + '.c'
        elif request.form['language'] == 'cpp':
            sourceSavedFilename = unique_id + '.cpp'
        elif request.form['language'] == 'pas':
            sourceSavedFilename = unique_id + '.pas'
        elif request.form['language'] == 'java':
            sourceSavedFilename = unique_id + '.java'
        elif request.form['language'] == 'py':
            sourceSavedFilename = unique_id + '.py'
        sourcefile.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], sourceSavedFilename))
        entry = Entry(
            _id=unique_id,
            author=session.get('username'),
            original_source=sourcefilename,
            language=request.form['language'],
            problem=request.form['problem'],
            grade=session.get('grade'),
            email=session.get('email'),
            date=datetime.datetime.utcnow())
        g.db.save_doc(entry)
        session['last_problem'] = request.form['problem']
        session['last_language'] = request.form['language']
        flash('Your problem was successfully uploaded.', 'success')
        return redirect(url_for('status'))
    flash('Invalid extension', 'danger')
    return redirect(url_for('status'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('grade', None)
    session.pop('admin', None)
    session.pop('last_problem', None)
    session.pop('last_language', None)
    flash('You were successfully logged out', 'success')
    return redirect(url_for('status'))


@app.route('/rankings/<problem>')
def generate_specific_rankings(problem):
    hideRanking = False
    if not session.get('admin') and isRankingClosed():
        hideRanking = True
    grade = session.get('grade')
    if problem not in app.config['PROBLEMS']:
        flash("Invalid problem name", 'danger')
        return redirect(url_for('status'))
    rankings = g.db.view('users/by_results', startkey=["%s" % problem], endkey=["%s" % problem, {}])
    if rankings.first():
        return render_template('rankings.html', rankings=rankings, hideRanking=hideRanking)
    flash("No rankings available for that problem yet", 'danger')
    return redirect(url_for('generate_rankings'))


@app.route('/rankings')
def generate_rankings():
    hideRanking = False
    if not session.get('admin') and isRankingClosed():
        hideRanking = True
    grade = session.get('grade')
    if not grade:
        abort(401)
    rankings = g.db.list("users/by_total", "users/by_total", group="true", group_level=3)
    if rankings:
        for entry in rankings:
            if entry['grade'] != grade and not session.get('admin'):
                rankings.remove(entry)
        return render_template('rankings.html', rankings=rankings, problems=app.config['PROBLEMS'], hideRanking=hideRanking)
    flash("There are no rankings available yet", 'danger')
    return redirect(url_for('status'))


@app.route('/rankings/export/all')
def export_rankings():
    if not session.get('admin'):
        abort(401)
    rankings = g.db.list("users/by_total", "users/by_total", group="true", group_level=3)
    if not rankings:
        flash("There are no rankings available yet", 'danger')
        return redirect(url_for('generate_rankings'))
    pd_rankings = pd.read_json(json.dumps(rankings))
    pd_rankings["points"] = pd_rankings["points"].apply(lambda x: x * -1)
    csv_rankings = pd_rankings.reindex(columns=["username", "grade", "points", "duration", "email"]).to_csv(index=False)
    output = make_response(csv_rankings)
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-Type"] = "text/csv"
    return output


@app.route('/rankings/export/detailed')
def export_rankings_detailed():
    if not session.get('admin'):
        abort(401)
    rankings = g.db.list("users/by_problem", "users/by_total", group="true", group_level=7)
    if not rankings:
        flash("There are no rankings available yet", 'danger')
        return redirect(url_for('generate_rankings'))
    pd_rankings = pd.read_json(json.dumps(rankings))
    pd_rankings["points"] = pd_rankings["points"].apply(lambda x: x * -1)
    csv_rankings = pd_rankings.reindex(columns=["username", "grade", "problem", "points", "duration", "language", "email"]).to_csv(index=False)
    output = make_response(csv_rankings)
    output.headers["Content-Disposition"] = "attachment; filename=export_detailed.csv"
    output.headers["Content-Type"] = "text/csv"
    return output


@app.route('/rankings/export/sources')
def export_rankings_sources():
    if not session.get('admin'):
        abort(401)
    uploads = g.db.view("users/by_uploads")
    if not uploads:
        flash("There are no uploads available yet", 'danger')
        return redirect(url_for('generate_rankings'))
    tmp_dirname = 'sources_' + str(uuid.uuid4())
    tmp_directory_path = os.path.join(basedir, app.config['UPLOAD_FOLDER'], tmp_dirname)
    os.mkdir(tmp_directory_path)
    for upload in uploads:
        extension = '.' + upload['value'][2]
        new_filename = upload['key'] + '_' + upload['value'][1] + '_' + upload['value'][4] + extension
        src_file = os.path.join(basedir, app.config['UPLOAD_FOLDER'], upload['id'] + extension)
        dest_file = os.path.join(tmp_directory_path, new_filename)
        try:
            copy2(src_file, dest_file)
        except IOError, e:
            print "Unable to copy file %s" % e
    make_archive(os.path.join(basedir, app.config['UPLOAD_FOLDER'], tmp_dirname), 'zip', base_dir=os.path.join(basedir, app.config['UPLOAD_FOLDER'], tmp_dirname))  # need to check why it creates full directory structure
    rmtree(tmp_directory_path)
    return send_from_directory(app.config['UPLOAD_FOLDER'], tmp_dirname + '.zip')



@app.route('/delete/<path:path>')
def delete_file(path):
    if isBeforeContest():
        return render_template('placeholder_before.html', countDownTo=openContest)
    if isAfterContest():
        return render_template('placeholder_after.html')
    if session.get('logged_in'):
        if session.get('admin'):
            files = g.db.view("users/by_uploads")
        else:
            files = g.db.view("users/by_uploads", key=session.get('username'))
        if files.first() or session.get('admin'):
            for file in files:
                if path in file['id']:
                    fileToRemove = os.path.join(basedir, app.config['UPLOAD_FOLDER'], path)
                    for f in glob.glob('%s*' % fileToRemove):
                        os.remove(f)
                    g.db.delete_doc(path)
                    flash("File successfully removed.", 'success')
                    return redirect(url_for('status'))
    flash("You are not authorized to do this.", 'danger')
    return redirect(url_for('status'))


def store_duration(path, stdout, failed=None):
    server = couchdbkit.Server(app.config['COUCHDB_URL'])
    db = server.get_or_create_db(app.config['DATABASE'])
    doc = db.get(path)
    if failed is None:
        concat = ''.join(stdout)
        total = float(stdout[-1].split(',')[0].strip('Total: '))
        points = int(stdout[-2].split(':')[1].strip())
        if 'tested' not in doc:
            doc['total'] = total
            doc['failed'] = failed
            doc['points'] = points * -1
            doc['stdout'] = concat
            doc['tested'] = 1
    else:
        doc['stdout'] = stdout
        doc['tested'] = 2
    db.save_doc(doc)
    return True


def number_of_tests(problem, grade):
    return len([name for name in os.listdir('%s/tests/%s' % (basedir, problem)) if name.startswith(grade) and os.path.isfile(os.path.join(basedir, 'tests', problem, name))]) / 2


def compare_files(fpath1, fpath2):
    with open(fpath1, 'r') as file1, open(fpath2, 'r') as file2:
        for linef1, linef2 in izip(file1, file2):
            linef1 = linef1.rstrip('\r\n')
            linef2 = linef2.rstrip('\r\n')
            if linef1 != linef2:
                return False
        return next(file1, None) is None and next(file2, None) is None


def run_tests(path, problem, language, grade, test_count):
    results = []
    total = 0
    failed = 0
    run_directory = working_directory + path
    for test in range(1, test_count + 1):
        for file_path in glob.glob(r'%s/tests/%s/%s-test%d.*' % (basedir, problem, grade, test)):
            filename, extension = file_path.split('.')
            dest_file = problem + '.' + extension
            copy2(file_path, os.path.join(working_directory, path, dest_file))
        if language == 'java':
            try:
                subprocess32.check_output(['java', 'Main'], cwd='%s' % run_directory, stderr=subprocess32.STDOUT, timeout=4)
            except (subprocess32.CalledProcessError, subprocess32.TimeoutExpired) as e:
                results.append('Execution error:')
                results.append(e.output)
                return results
            stmt = """\
try:
    subprocess32.check_output(['java', 'Main'], cwd='%s', stderr=subprocess32.STDOUT, timeout=4)
except (subprocess32.CalledProcessError, subprocess32.TimeoutExpired):
    pass""" % run_directory
        elif language == 'py':
            try:
                subprocess32.check_output(['python', '%s.py' % problem], cwd='%s' % run_directory, stderr=subprocess32.STDOUT, timeout=4)
            except (subprocess32.CalledProcessError, subprocess32.TimeoutExpired) as e:
                results.append('Execution error:')
                results.append(e.output)
                return results
            stmt = """\
try:
    subprocess32.check_output(['python', '%s.py'], cwd='%s', stderr=subprocess32.STDOUT, timeout=4)
except (subprocess32.CalledProcessError, subprocess32.TimeoutExpired):
    pass""" % (problem, run_directory)
        else:
            try:
                subprocess32.check_output(['./%s' % problem], cwd='%s' % run_directory, stderr=subprocess32.STDOUT, timeout=4)
            except (subprocess32.CalledProcessError, subprocess32.TimeoutExpired) as e:
                results.append('Execution error:')
                results.append(e.output)
                return results
            stmt = """\
try:
    subprocess32.check_output(['./%s'], cwd='%s', stderr=subprocess32.STDOUT, timeout=4)
except (subprocess32.CalledProcessError, subprocess32.TimeoutExpired):
    pass""" % (problem, run_directory)
        time_elapsed = timeit(stmt=stmt, setup="import subprocess32", number=3) / 3
        try:
            if compare_files('%s/%s/%s.out' % (working_directory, path, problem), '%s/%s/%s.ok' % (working_directory, path, problem)):
                results.append('Test {:d} PASSED in {:.3f} seconds\n'.format(test, time_elapsed))
                total += time_elapsed
            else:
                results.append('Test {:d} FAILED in {:.3f} seconds\n'.format(test, time_elapsed))
                total += time_elapsed
                points = (test - 1) * 5
                results.append('Points: {:d}\n'.format(points))
                if time_elapsed >= 4:
                    results.append('Total: {:.3f}, Stopped because of timeout (over 4 sec/test).'.format(total, failed))
                else:
                    results.append('Total: {:.3f}, Stopped because of failure.'.format(total, failed))
                return results
        except IOError:
            results.append('Error. Check output filename')
            return results
    points = (test_count - failed) * 5
    results.append('Points: {:d}\n'.format(points))
    results.append('Total: {:.3f}, Failed: {:d}'.format(total, failed))
    return results


@celery.task(bind=True)
def run_task(self, path, problem, language, grade):
    if os.path.exists(os.path.join(working_directory, path)):
        rmtree(os.path.join(working_directory, path))
    unique_path = os.path.join(basedir, app.config['UPLOAD_FOLDER'], path)
    os.makedirs(os.path.join(working_directory, path))
    if language == 'c':
        sourcefile = unique_path + '.c'
        copy2(sourcefile, os.path.join(working_directory, path, '%s.c' % problem))
        try:
            subprocess32.check_output(['gcc', '-Wall', '-O2', '-static', '%s.c' % problem, '-I.', '-o', '%s' % problem], stderr=subprocess32.STDOUT, cwd=os.path.join(working_directory, path))
        except subprocess32.CalledProcessError, e:
            store_duration(path, e.output, 1)
            return {'status': e.output,
                    'result': 'Compilation error'}
    elif language == 'cpp':
        sourcefile = unique_path + '.cpp'
        copy2(sourcefile, os.path.join(working_directory, path, '%s.cpp' % problem))
        try:
            subprocess32.check_output(['g++', '-std=c++11', '-Wall', '-O2', '-static', '%s.cpp' % problem, '-I.', '-o', '%s' % problem], stderr=subprocess32.STDOUT, cwd=os.path.join(working_directory, path))
        except subprocess32.CalledProcessError, e:
            store_duration(path, e.output, 1)
            return {'status': e.output,
                    'result': 'Compilation error'}
    elif language == 'pas':
        sourcefile = unique_path + '.pas'
        copy2(sourcefile, os.path.join(working_directory, path, '%s.pas' % problem))
        try:
            subprocess32.check_output(['fpc', '-O2', '-Xs', '%s.pas' % problem, '-o%s' % problem], stderr=subprocess32.STDOUT, cwd=os.path.join(working_directory, path))
        except subprocess32.CalledProcessError, e:
            store_duration(path, e.output, 1)
            return {'status': e.output,
                    'result': 'Compilation error'}
    elif language == 'java':
        sourcefile = unique_path + '.java'
        copy2(sourcefile, os.path.join(working_directory, path, 'Main.java'))
        try:
            subprocess32.check_output(['javac', 'Main.java'], stderr=subprocess32.STDOUT, cwd=os.path.join(working_directory, path))
        except subprocess32.CalledProcessError, e:
            store_duration(path, e.output, 1)
            return {'status': e.output,
                    'result': 'Compilation error'}
    elif language == 'py':
        sourcefile = unique_path + '.py'
        copy2(sourcefile, os.path.join(working_directory, path, '%s.py' % problem))
    stdout = run_tests(path, problem, language, grade, number_of_tests(problem, grade))
    if 'Error. Check output filename' in stdout or 'Execution error:' in stdout:
        store_duration(path, stdout, 1)
    else:
        store_duration(path, stdout)
    #rmtree(os.path.join(working_directory, path))
    return {'status': stdout,
            'result': 'Task completed!'}


@app.route('/run/<path:path>', methods=['POST'])
def runtask(path):
    if isBeforeContest():
        return render_template('placeholder_before.html', countDownTo=openContest)
    if isAfterContest():
        return render_template('placeholder_after.html')
    info = g.db.view("users/by_uploads", key=session.get('username'))
    for f in info:
        if path in f['id']:
            problem = f['value'][1]
            language = f['value'][2]
    run_task.apply_async(args=[path, problem, language, session.get('grade')], task_id=path)
    return jsonify({}), 202, {'Location': url_for('taskstatus', path=path)}


@app.route('/status/<path:path>')
def taskstatus(path):
    if isBeforeContest():
        return render_template('placeholder_before.html', countDownTo=openContest)
    if isAfterContest():
        return render_template('placeholder_after.html')
    task = run_task.AsyncResult(path)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Your task has been placed in the queue and is running. Be patient...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'status': str(task.info),
        }
    return jsonify(response)


app.debug = True
app.logger.setLevel(logging.INFO)
couchdbkit.set_logging('info')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
