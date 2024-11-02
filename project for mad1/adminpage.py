import sqlite3
from flask import Blueprint, jsonify, render_template, request, redirect, url_for,flash
from werkzeug.utils import secure_filename
import os
from creator import get_creator_count,get_creator_emails

adminpage_bp = Blueprint('adminpage_bp', __name__, static_folder='static', template_folder='templates')

def query_song_db(query, args=(), one=False):
    with sqlite3.connect('song.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        result = cursor.execute(query, args).fetchone() if one else cursor.execute(query, args).fetchall()
    return result

@adminpage_bp.route('/adminpage', methods=['GET'])
def adminpage():
    
    from app import get_total_song_count
    from album import get_existing_albums
    table_names = ["songlist4", "songlist2","songs"]
    query = " UNION ".join([f"SELECT image_path, song_name, file_path FROM {table_name}" for table_name in table_names])
    all_songs = query_song_db(f"{query} ORDER BY song_name")
    total_count = get_total_song_count()
    existing_albums = get_existing_albums()
    return render_template('adminpage.html', all_songs=all_songs,total_count=total_count,existing_albums=existing_albums)


adminpage_bp = Blueprint('adminpage', __name__, static_folder='static', template_folder='templates')

def query_song_db(query, args=(), one=False):
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

@adminpage_bp.route('/remove_song/<int:song_id>', methods=['POST'])
def remove_song(song_id):
    try:
        connection = sqlite3.connect('song.db')
        cursor = connection.cursor()

        cursor.execute('DELETE FROM songs WHERE id = ?', (song_id,))
        connection.commit()
        connection.close()

        return redirect(url_for('adminpage.adminpage'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@adminpage_bp.route('/adminpage', methods=['GET'])
def adminpage():
    from app import get_total_song_count,get_total_album_count
    from album import get_existing_albums
    from login import get_user_count
    from creator import get_creator_count
    table_names = ["songlist4", "songlist2", "songs"]
    query = " UNION ".join([f"SELECT image_path, song_name, file_path, id FROM {table_name}" for table_name in table_names])
    all_songs = query_song_db(f"{query} ORDER BY song_name")
    total_count = get_total_song_count()
    existing_albums = get_existing_albums()
    album_count=get_total_album_count()
    creator_count=get_creator_count()
    user_count=get_user_count()
    
    return render_template('adminpage.html', all_songs=all_songs, total_count=total_count, existing_albums=existing_albums,album_count=album_count,creator_count=creator_count,user_count=user_count)



@adminpage_bp.route('/get_all_creators', methods=['GET'], endpoint='get_all_creators')
def get_all_creators():
    search_query = request.args.get('search_query', '')

    creator_emails = get_creator_emails(search_query)

    email_blacklisted = get_email_blacklisted_status(creator_emails)

    return render_template('creator_emails.html', creator_emails=creator_emails, email_blacklisted=email_blacklisted)


def get_creator_emails(search_query=''):
    query = 'SELECT email FROM creator'
    if search_query:
        query += f" WHERE email LIKE '%{search_query}%'"
    with sqlite3.connect('song.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        creator_emails = [row[0] for row in cursor.fetchall()]
    return creator_emails

def get_email_blacklisted_status(emails):
    query = 'SELECT email, blacklisted FROM creator WHERE email IN ({})'.format(','.join(['?']*len(emails)))
    with sqlite3.connect('song.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(emails))
        email_blacklisted = {row[0]: row[1] for row in cursor.fetchall()}
    return email_blacklisted


@adminpage_bp.route('/blacklist_creator/<string:email>', methods=['POST'])
def blacklist_creator(email):
    update_blacklist_status(email, True)
    return redirect(url_for('adminpage.get_all_creators'))

@adminpage_bp.route('/unblacklist_creator/<string:email>', methods=['POST'])
def unblacklist_creator(email):
    update_blacklist_status(email, False)
    return redirect(url_for('adminpage.get_all_creators'))

def update_blacklist_status(email, is_blacklisted):
    query = 'UPDATE creator SET blacklisted = ? WHERE email = ?'
    with sqlite3.connect('song.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, (is_blacklisted, email))
        conn.commit()
