import sqlite3
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session

playlist = Blueprint('playlist', __name__, static_folder='static', template_folder='templates')

def create_tables():
    connection = sqlite3.connect('song.db')
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES login (id)    
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlist_songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER,
            song_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            image_path TEXT NOT NULL,
            FOREIGN KEY (playlist_id) REFERENCES playlists (id)
        )
    ''')

    connection.commit()
    connection.close()

def add_playlist(playlist_name, user_id):
    try:
        connection = sqlite3.connect('song.db')
        cursor = connection.cursor()

        cursor.execute('INSERT INTO playlists (user_id, name) VALUES (?, ?)', (user_id, playlist_name))
        connection.commit()
        connection.close()

        return jsonify({'message': 'Playlist added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

create_tables()



def get_playlist_name(playlist_id):
    connection = sqlite3.connect('song.db')
    cursor = connection.cursor()

    cursor.execute('SELECT name FROM playlists WHERE id = ?', (playlist_id,))
    playlist_name = cursor.fetchone()[0]

    connection.close()
    return playlist_name

@playlist.route('/playlist', methods=['GET', 'POST'])
def playlist_page():
    user_id = session.get('user_id')
    print(f"user_id_from_session: {user_id}")

    if request.method == 'POST':
        playlist_name = request.form.get('playlist_name')
        if playlist_name and user_id:
            add_playlist(playlist_name, user_id)

    existing_playlists = get_existing_playlists(user_id)

    return render_template('playlist.html', user_id=user_id, existing_playlists=existing_playlists)



def get_songs_for_playlist(playlist_id):
    connection = sqlite3.connect('song.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id, song_name, file_path, image_path FROM playlist_songs WHERE playlist_id = ?', (playlist_id,))
    songs = [{'id': row[0], 'song_name': row[1], 'file_path': row[2], 'image_path': row[3]} for row in cursor.fetchall()]

    connection.close()
    return songs

def get_existing_playlists(user_id):
    connection = sqlite3.connect('song.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id, name FROM playlists WHERE user_id = ?', (user_id,))
    playlists = [{'id': row[0], 'name': row[1], 'songs': get_songs_for_playlist(row[0])} for row in cursor.fetchall()]

    connection.close()
    return playlists

@playlist.route('/remove_song1/<int:song_id>', methods=['POST'])
def remove_song(song_id):
    user_id = session.get('user_id')
    try:
        connection = sqlite3.connect('song.db')
        cursor = connection.cursor()

        cursor.execute('DELETE FROM playlist_songs WHERE id = ?', (song_id,))
        connection.commit()
        connection.close()

        return redirect(url_for('playlist.playlist_page', user_id=user_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@playlist.route('/update_playlist/<int:playlist_id>', methods=['POST'])
def update_playlist(playlist_id):
    if request.method == 'POST':
        new_playlist_name = request.form.get('new_playlist_name')
        user_id = request.form.get('user_id') 

        connection = sqlite3.connect('song.db')
        cursor = connection.cursor()

        cursor.execute('UPDATE playlists SET name = ? WHERE id = ?', (new_playlist_name, playlist_id))
        connection.commit()
        connection.close()

        return redirect(url_for('playlist.playlist_page', user_id=user_id))
    

@playlist.route('/delete_playlist/<int:playlist_id>', methods=['POST'])
def delete_playlist(playlist_id):
    if request.method == 'POST':
        user_id = request.form.get('user_id')
    try:
        connection = sqlite3.connect('song.db')
        cursor = connection.cursor()

        cursor.execute('DELETE FROM playlists WHERE id = ?', (playlist_id,))
        cursor.execute('DELETE FROM playlist_songs WHERE playlist_id = ?', (playlist_id,))

        connection.commit()
        connection.close()

        return redirect(url_for('playlist.playlist_page'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@playlist.route('/add_to_playlist/<int:playlist_id>', methods=['POST'])
def add_to_playlists(playlist_id):
    try:
        data = request.get_json()
        song_name = data.get('song_name')
        file_path = data.get('file_path')
        image_path = data.get('image_path')

        connection = sqlite3.connect('song.db')
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO playlist_songs (playlist_id, song_name, file_path, image_path)
            VALUES (?, ?, ?, ?)
        ''', (playlist_id, song_name, file_path, image_path))

        connection.commit()
        connection.close()

        return jsonify({'message': 'Song added to playlist successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
