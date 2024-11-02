from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3

admin = Blueprint('admin', __name__, static_folder='static', template_folder='templates')


def create_admin_table():
    connection = sqlite3.connect('song.db')
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    connection.commit()
    connection.close()

create_admin_table()

def query_admin_db(query, args=(), one=False):
    with sqlite3.connect('song.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        result = cursor.execute(query, args).fetchone() if one else cursor.execute(query, args).fetchall()
    return result

@admin.route("/admin", methods=['GET','POST'])
def admin_route():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        action = request.form.get('action')

        if action == 'admin': 
            user = query_admin_db('SELECT * FROM admins WHERE email = ? AND password = ?', (email, password), one=True)

            if user:
                return redirect(url_for('adminpage.adminpage'))
            else:
                return render_template('admin.html', error='Invalid credentials')

    return render_template('admin.html')

