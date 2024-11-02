from flask import Blueprint, render_template, request
import sqlite3

search = Blueprint('search', __name__, static_folder='static', template_folder='templates')

def query_song_db(query, args=(), one=False):
    with sqlite3.connect('song.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        result = cursor.execute(query, args).fetchone() if one else cursor.execute(query, args).fetchall()
    return result

@search.route('/search', methods=['GET', 'POST'])
def search_song():
    if request.method == 'POST':
        search_term = request.form.get('search_term')
      
        table_names = ["songlist1", "songlist2", "songlist3", "songlist4", 'songs']
    
        query = " UNION ".join([f"SELECT image_path, song_name, file_path FROM {table_name} WHERE song_name LIKE ?" for table_name in table_names])
        
        placeholders = " OR ".join(["?" for _ in table_names])
        
        songs_list = query_song_db(f"{query} ORDER BY song_name", tuple(f"%{search_term}%" for _ in table_names))

        
        return render_template('search_results.html', songs_list=songs_list, search_term=search_term)
    
    return render_template('search_results.html')
