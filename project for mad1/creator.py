from flask import Blueprint, render_template, request, redirect, url_for,session
import sqlite3
from login import query_login_db

creator = Blueprint('creator', __name__, static_folder='static', template_folder='templates')

def create_login_table():
    try:
        with sqlite3.connect('song.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS creator (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    blacklisted INTEGER DEFAULT 0    
                )
            ''')
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

create_login_table()

def get_creator_count():
    query = 'SELECT COUNT(*) FROM creator'
    with sqlite3.connect('song.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        creator_count = cursor.fetchone()[0]
    return creator_count

def get_creator_emails():
    query = 'SELECT email FROM creator'
    with sqlite3.connect('song.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        creator_emails = [row[0] for row in cursor.fetchall()]
    return creator_emails

@creator.route("/creator", methods=['GET', 'POST'])
def creator_signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        action = request.form.get('action')

        if action == 'signup':
            existing_user = query_login_db('SELECT * FROM creator WHERE email = ?', (email,), one=True)

            if existing_user:
                if existing_user['password'] == password:
                    blacklisted_status = existing_user['blacklisted']

                    if blacklisted_status != 0:
                        return render_template('creator.html', warning='Sorry, your account has been blacklisted. Contact support for assistance.')

                    new_users = query_login_db('SELECT * FROM creator WHERE email = ?', (email,), one=True)
                    session['creator_id']=new_users['id']
                    return redirect(url_for('album.album_page', creator_id=new_users['id']))
            else:
                
                try:
                    with sqlite3.connect('song.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO creator (email, password) VALUES (?, ?)', (email, password))
                        conn.commit()
                        new_users = query_login_db('SELECT * FROM creator WHERE email = ?', (email,), one=True)
                        session['creator_id']=new_users['id']
                    return redirect(url_for('album.album_page', creator_id=new_users['id']))

                except sqlite3.Error as e:
                      print(f"Error inserting new row: {e}")
                      return render_template('creator.html', warning='An error occurred during signup. Please try again.')


    return render_template('creator.html')
