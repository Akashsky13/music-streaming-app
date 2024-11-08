from flask import Flask, render_template, request, session, redirect, url_for, jsonify,flash

import sqlite3
from login import login
from search import search

from admin import admin
from signup import signup
from creator import creator
from playlist import playlist
from adminpage import adminpage_bp
from album import album
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_DATABASE'] = 'song.db'
app.config['UPLOAD_FOLDER'] = 'static'
app.secret_key = 'your_secret_key'
app.register_blueprint(search)
app.register_blueprint(login)
app.register_blueprint(adminpage_bp)
app.register_blueprint(creator)
app.register_blueprint(admin)
app.register_blueprint(signup)
app.register_blueprint(playlist)
app.register_blueprint(album) 


def create_songlist_table():
    with sqlite3.connect('song.db') as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                genre TEXT NOT NULL,
                artist TEXT NOT NULL
                
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                album_id INTEGER,
                song_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                image_path TEXT NOT NULL,
                average_rating REAL DEFAULT 0,
                FOREIGN KEY (album_id) REFERENCES albums (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS song_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id INTEGER,
                rating INTEGER,
                FOREIGN KEY (song_id) REFERENCES songs (id)
            )
        ''')
def query_songlist_db(query, args=(), one=False):
    with sqlite3.connect('song.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        result = cursor.execute(query, args).fetchone() if one else cursor.execute(query, args).fetchall()
    return result

def execute_songlist_db(query, args=()):
    with sqlite3.connect('song.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()

create_songlist_table()

def get_total_song_count():
    
    count5 = len(query_songlist_db("SELECT * FROM songs"))
    return count5


def get_total_album_count():
    query = "SELECT COUNT(*) FROM albums"
    result = query_songlist_db(query, one=True)
    total_album_count = result[0] if result else 0
    return total_album_count
@app.route('/')
def base():
    return render_template('base.html')


@app.route("/index")
def index():
    from playlist import get_existing_playlists
    from album import get_existing_album
    

    user_id = session.get('user_id')
    first_name = session.get('first_name')
    
    creator_id = session.get('creator_id')
    
    songs_list6 = query_songlist_db("SELECT * FROM songs")

    total_count = get_total_song_count()
    album_count=get_total_album_count()
    existing_playlists = get_existing_playlists(user_id)
    existing_albums = get_existing_album()
    
    return render_template('index.html', total_count=total_count, existing_playlists=existing_playlists, existing_albums=existing_albums, songs_list6=songs_list6, user_id=user_id, album_count=album_count, first_name=first_name, creator_id=creator_id)

@app.route("/logout", methods=['GET'])
def logout_route():
    
    user_email = session.get('user_email')
    delete_user_query = 'DELETE FROM loginfo WHERE email = ?'
    with sqlite3.connect('login.db') as conn:
        cursor = conn.cursor()
        cursor.execute(delete_user_query, (user_email,))
        conn.commit()

    
    return redirect(url_for('login.login_route'))

if __name__ == "__main__":
    app.run(debug=True)
