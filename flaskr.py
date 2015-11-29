# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


# create our little application :)
app = Flask(__name__)


# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select * from button_press order by pressed_at desc')
    entries = [dict((key, row[key]) for key in row.keys()) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=json.dumps(entries))


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
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
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


@app.route('/api/button/<carriage>-<seat_number>')
def button(carriage, seat_number):
    db = get_db()
    db.execute('insert into button_press (carriage, seat_number, pressed_at) values (?, ?, ?)',
               [carriage, seat_number, datetime.today().strftime('%Y-%m-%d %H:%M:%S')])
    db.commit()

    return "You pressed the button {} {}".format(carriage, seat_number)


@app.route('/api/list')
def api_list():
    db = get_db()
    cur = db.execute('select * from button_press order by pressed_at desc')
    entries = [dict((key, row[key]) for key in row.keys()) for row in cur.fetchall()]
    return json.dumps(entries)

if __name__ == "__main__":
    app.run()
