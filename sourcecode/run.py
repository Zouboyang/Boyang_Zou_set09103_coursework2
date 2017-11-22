from flask import Flask, g, session, render_template, flash, redirect, url_for, request
import sqlite3

from flask import Flask

SECRET_KEY = 'NIMABI'
USERNAME = 'Zouboyang'
PASSWORD = 'default'
app = Flask(__name__)
app.config.from_object(__name__)
db_location = 'var/zby.db'


def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = sqlite3.connect(db_location)
        g.db = db
    return db

@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = get_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/', methods=['POST', 'GET'])
def index():
    
    return render_template('index.html')

@app.route('/products/')
def products():
    return render_template('products.html')

@app.route('/sign_up/')
def sign_up():
    return render_template('register.html')


@app.route('/contact/')
def contact():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('contact.html', entries=entries)

@app.route('/add/', methods=['POST'])
def add_entry():
    
    g.db.execute('insert into entries (title, text) values (?, ?)',[request.form['title'], request.form['text']])
    g.db.commit()
    
    return redirect(url_for('contact'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index', username=request.form['username']))
    return render_template('login.html', error=error,)

@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html'), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)