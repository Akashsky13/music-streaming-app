from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
from login import query_login_db

creator = Blueprint('creator', __name__, static_folder='static', template_folder='templates')

def create_login_table():
    try:
        with sqlite3.connect('song.db') as conn:
            cursor = conn.cursor()
            # Create the table if it does not exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS creator (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')

            # Check if blacklisted column exists, add it if it doesn't
            cursor.execute("PRAGMA table_info(creator)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'blacklisted' not in columns:
                cursor.execute("ALTER TABLE creator ADD COLUMN blacklisted INTEGER DEFAULT 0")
                conn.commit()

    except sqlite3.Error as e:
        print(f"Error creating or modifying table: {e}")

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

                    # Check if user is blacklisted
                    if blacklisted_status != 0:
                        # Show a warning message if blacklisted
                        return render_template('creator.html', warning='Your account is blacklisted. Please contact support.')

                    # User is not blacklisted; proceed with login
                    session['creator_id'] = existing_user['id']
                    return redirect(url_for('album.album_page', creator_id=existing_user['id']))
                else:
                    return render_template('creator.html', warning='Incorrect password. Please try again.')
            else:
                # New user registration
                try:
                    with sqlite3.connect('song.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO creator (email, password) VALUES (?, ?)', (email, password))
                        conn.commit()
                        new_user = query_login_db('SELECT * FROM creator WHERE email = ?', (email,), one=True)
                        session['creator_id'] = new_user['id']
                    return redirect(url_for('album.album_page', creator_id=new_user['id']))

                except sqlite3.Error as e:
                    print(f"Error inserting new row: {e}")
                    return render_template('creator.html', warning='An error occurred during signup. Please try again.')

    return render_template('creator.html')
