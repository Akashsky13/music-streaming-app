from flask import Blueprint, render_template, request, redirect, url_for,session
import sqlite3
from login import query_login_db

signup = Blueprint('signup', __name__, static_folder='static', template_folder='templates')


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

create_login_table()

@signup.route("/signup", methods=['GET', 'POST'])
def signup_route():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        age = request.form.get('age')
        action = request.form.get('action')

        if action == 'signup':
            
            existing_user = query_login_db('SELECT * FROM login WHERE email = ?', (email,), one=True)

            if existing_user is not None:
                session['user_id'] = existing_user['id']
                session['first_name'] = existing_user['first_name']
                return render_template('signup.html', error='User with this email already exists. Please use a different email.')
            else:
                with sqlite3.connect('song.db') as conn:
                    cursor = conn.cursor()
                    # Update the SQL query to include additional details
                    cursor.execute('INSERT INTO login (email, password, first_name, last_name, age) VALUES (?, ?, ?, ?, ?)',
                                   (email, password, first_name, last_name, age))
                    conn.commit()
                    
                    # Fetch the newly created user from the database
                    new_user = query_login_db('SELECT * FROM login WHERE email = ?', (email,), one=True)
                    session['first_name']=new_user['first_name']
                    session['user_id']=new_user['id']
                return redirect(url_for('index', user_id=new_user['id']))

    return render_template('signup.html')
