import sqlite3
from flask import Blueprint, jsonify, render_template, request, redirect, url_for,session
from werkzeug.utils import secure_filename
import os
album = Blueprint('album', __name__, static_folder='static', template_folder='templates')

# Create SQLite database and albums table
def create_tables():
    connection = sqlite3.connect('song.db')
    cursor = connection.cursor()


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS albums (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER,
            name TEXT NOT NULL,
            genre TEXT NOT NULL,
            artist TEXT NOT NULL,
            FOREIGN KEY (creator_id) REFERENCES creator (id)
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

    connection.commit()
    connection.close()

def get_album_name(album_id):
    connection = sqlite3.connect('song.db')
    cursor = connection.cursor()

    cursor.execute('SELECT name FROM albums WHERE id = ?', (album_id,))
    result = cursor.fetchone()
    album_name = result[0] if result else None

    connection.close()
    return album_name



def add_album(album_name, genre, artist):
    try:
        creator_id = session.get('creator_id')
        print(f"Debug: creator_id - {creator_id}, album_name - {album_name}, genre - {genre}, artist - {artist}")

        connection = sqlite3.connect('song.db')
        cursor = connection.cursor()

        cursor.execute('INSERT INTO albums (creator_id, name, genre, artist) VALUES (?, ?, ?, ?)', (creator_id, album_name, genre, artist))
        connection.commit()
        connection.close()

        return jsonify({'message': 'album added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

create_tables()
       
def get_existing_albums():
    # Assuming you get creator_id from the session
    creator_id = session.get('creator_id')
    
    connection = sqlite3.connect('song.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id, name, genre, artist FROM albums WHERE creator_id = ?', (creator_id,))
    
    albums = [{'id': row[0], 'name': row[1], 'genre': row[2], 'artist': row[3], 'songs': get_songs_for_album(row[0]), 'average_album_rating': get_album_average_rating(row[0])} for row in cursor.fetchall()]

    connection.close()
    return albums
def get_existing_album():
    # Assuming you get creator_id from the session
    
    
    connection = sqlite3.connect('song.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM albums')
    
    albums = [{'id': row[0], 'name': row[2], 'genre': row[3], 'artist': row[4], 'songs': get_songs_for_album(row[0]), 'average_album_rating': get_album_average_rating(row[0])} for row in cursor.fetchall()]

    connection.close()
    return albums

@album.route("/album", methods=['GET', 'POST'])
def album_page():
    creator_id = session.get('creator_id')
    print(f"user_id_from_session: {creator_id}")
    if request.method == 'POST':
        album_name = request.form.get('album_name')
        genre = request.form.get('genre') 
        artist = request.form.get('artist')  

        if album_name and genre and artist:
            creator_id = session.get('creator_id')
            print(f"Debug: creator_id - {creator_id}, album_name - {album_name}, genre - {genre}, artist - {artist}")
            add_album(album_name, genre, artist) 

    existing_albums = get_existing_albums()
    
    return render_template('album.html', creator_id=creator_id, existing_albums=existing_albums)




def get_songs_for_album(album_id):
    connection = sqlite3.connect('song.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id, song_name, file_path, image_path FROM songs WHERE album_id = ?', (album_id,))
    
    songs = []
    for row in cursor.fetchall():
        song_id = row[0]
        song_name = row[1]
        file_path = row[2]
        image_path = row[3]

        song_average_rating = get_average_rating(song_id)

        songs.append({
            'id': song_id,
            'song_name': song_name,
            'file_path': file_path,
            'image_path': image_path,
            'average_rating': song_average_rating
        })

    connection.close()
    return songs

@album.route('/remove_songs/<int:song_id>', methods=['POST'])
def remove_song(song_id):
    creator_id = session.get('creator_id')
    try:
        connection = sqlite3.connect('song.db')
        cursor = connection.cursor()

        cursor.execute('DELETE FROM songs WHERE id = ?', (song_id,))
        connection.commit()
        connection.close()

        return redirect(url_for('album.album_page', creator_id=creator_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@album.route('/update_album/<int:album_id>', methods=['POST'])
def update_album(album_id):
    creator_id = session.get('creator_id') 
    try:
        new_album_name = request.form.get('new_album_name')

        connection = sqlite3.connect('song.db')
        cursor = connection.cursor()

        cursor.execute('UPDATE albums SET name = ? WHERE id = ?', (new_album_name, album_id))
        connection.commit()
        connection.close()

        return redirect(url_for('album.album_page', creator_id=creator_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@album.route('/delete_album/<int:album_id>', methods=['POST'])
def delete_album(album_id):
    creator_id = session.get('creator_id')
    try:
        connection = sqlite3.connect('song.db')
        cursor = connection.cursor()
        cursor.execute('DELETE FROM albums WHERE id = ?', (album_id,))
        cursor.execute('DELETE FROM songs WHERE album_id = ?', (album_id,))
        connection.commit()
        connection.close()

        return redirect(url_for('album.album_page', creator_id=creator_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@album.route('/add_to_album/<int:album_id>', methods=['POST'])
def add_to_album(album_id):
    creator_id = session.get('creator_id')
    try:
        song_name = request.form.get('song_name')
        file_path = save_file(request.files['file_path'], 'songs', allowed_extensions=['mp3'])
        image_path = save_file(request.files['image_path'], 'images', allowed_extensions=['jpg'])

        connection = sqlite3.connect('song.db')
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO songs (album_id, song_name, file_path, image_path)
            VALUES (?, ?, ?, ?)
        ''', (album_id, song_name, file_path, image_path))
        cursor.execute('SELECT id FROM songs WHERE album_id = ? AND song_name = ?', (album_id, song_name))
        song_id = cursor.fetchone()[0]

    
        cursor.execute('INSERT INTO song_ratings (song_id, rating) VALUES (?, 0)', (song_id,))
    

        connection.commit()
        connection.close()

        return redirect(url_for('album.album_page', creator_id=creator_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500



def save_file(file, folder, allowed_extensions):
    if file:
        if allowed_file(file.filename, allowed_extensions):
            filename = secure_filename(file.filename)
            file_directory = os.path.join('static', folder)
            os.makedirs(file_directory, exist_ok=True)  # Create the directory if it doesn't exist
            file_path = os.path.join(file_directory, filename)
            file.save(file_path)
            return file_path
        else:
            raise ValueError('Invalid file type')
    else:
        return None

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@album.route('/update_song/<int:song_id>', methods=['POST'])
def update_song(song_id):
    creator_id = session.get('creator_id')
    try:
        new_song_name = request.form.get('new_song_name')
        new_song_image = request.files.get('new_song_image')
        new_song_file = request.files.get('new_song_file')

        connection = sqlite3.connect('song.db')
        cursor = connection.cursor()

       
        cursor.execute('SELECT * FROM songs WHERE id = ?', (song_id,))
        song_data = cursor.fetchone()

        if song_data:
            if new_song_name:
                cursor.execute('UPDATE songs SET song_name = ? WHERE id = ?', (new_song_name, song_id))

            if new_song_image:
                image_path = save_file(new_song_image, 'images', allowed_extensions=['jpg'])
                cursor.execute('UPDATE songs SET image_path = ? WHERE id = ?', (image_path, song_id))

            if new_song_file:
                file_path = save_file(new_song_file, 'songs', allowed_extensions=['mp3'])
                cursor.execute('UPDATE songs SET file_path = ? WHERE id = ?', (file_path, song_id))

            connection.commit()
            connection.close()

            return redirect(url_for('album.album_page', creator_id=creator_id))
        else:
            return jsonify({'error': 'Song not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_average_rating(song_id):
    try:
        connection = sqlite3.connect('song.db')
        cursor = connection.cursor()

        cursor.execute('''
            SELECT AVG(rating) 
            FROM song_ratings 
            WHERE song_id = ? 
                AND song_id IN (SELECT id FROM songs WHERE id = ?)
        ''', (song_id, song_id))

        average_rating = cursor.fetchone()[0] or 0

        connection.close()
        return average_rating
    except Exception as e:
        print(f"Error getting average rating for song ID {song_id}: {str(e)}")
        return 0 
def get_album_average_rating(album_id):
    connection = sqlite3.connect('song.db')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT AVG(s.avg_rating) 
        FROM (SELECT song_id, AVG(rating) as avg_rating FROM song_ratings GROUP BY song_id) as s
        JOIN songs ON s.song_id = songs.id
        WHERE songs.album_id = ?
    ''', (album_id,))
    album_average_rating = cursor.fetchone()[0] or 0

    connection.close()
    return album_average_rating



@album.route('/update_rating/<int:song_id>', methods=['POST'])
def update_rating(song_id):
    try:
        new_rating = int(request.form.get('new_rating'))

        with sqlite3.connect('song.db') as connection:
            cursor = connection.cursor()

            # Check if there is an existing rating entry
            cursor.execute('SELECT * FROM song_ratings WHERE song_id = ?', (song_id,))
            existing_entry = cursor.fetchone()

            if existing_entry:
                # Update the existing rating entry
                cursor.execute('UPDATE song_ratings SET rating = ? WHERE song_id = ?', (new_rating, song_id))
            else:
                # Insert a new rating entry
                cursor.execute('INSERT INTO song_ratings (song_id, rating) VALUES (?, ?)', (song_id, new_rating))

            # Update the average rating in the songs table
            cursor.execute('UPDATE songs SET average_rating = ? WHERE id = ?', (get_average_rating(song_id), song_id))

        print(f"Rating updated successfully for song ID {song_id} to {new_rating}")

        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error updating rating for song ID {song_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
  