from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3

login = Blueprint('login', __name__, static_folder='static', template_folder='templates')

def create_login_table():
    with sqlite3.connect('song.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                age INTEGER
            )
        ''')

def create_creator_table():
    with sqlite3.connect('song.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS creator (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
                
            )
        ''')

create_login_table()
create_creator_table()

def query_login_db(query, args=(), one=False):
    with sqlite3.connect('song.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        result = cursor.execute(query, args).fetchone() if one else cursor.execute(query, args).fetchall()
    return result
def get_user_count():
    query = 'SELECT COUNT(*) FROM login'
    with sqlite3.connect('song.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        user_count = cursor.fetchone()[0]
    return user_count
def count_rows(table_name):
    with sqlite3.connect('song.db') as conn:
        cursor = conn.cursor()
        result = cursor.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()
    return result[0]

def login_user(email, password, table_name):
    user = query_login_db(f'SELECT * FROM {table_name} WHERE email = ? AND password = ?', (email, password), one=True)
    return user

@login.route("/login", methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        action = request.form.get('action')

        if action == 'login':
            # Check the login table
            user = login_user(email, password, 'login')

            if user:
                # Set the user_id and user_email in the session
                session['user_id'] = user['id']
                session['first_name'] = user['first_name']
                session['user_email'] = user['email']
                # Redirect to the index page
                return redirect(url_for('index', user_id=user['id']))

            else:
                # If not found in login table, check the creator table
                creator = login_user(email, password, 'creator')

                if creator:
                    # Set the creator_id in the session
                    session['creator_id'] = creator['id']
                    # Redirect to the index page
                    return redirect(url_for('index', creator_id=creator['id']))
                
                # If not found in either table, show an error
                return render_template('login.html', error='Invalid credentials')

    row_count_login = count_rows('login')
    row_count_creator = count_rows('creator')
    return render_template('login.html', row_count_login=row_count_login, row_count_creator=row_count_creator)