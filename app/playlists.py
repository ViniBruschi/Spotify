import os, requests, psycopg2
from dotenv import load_dotenv
from spotify_credentials import client_id, client_secret, getAccessToken

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getPlaylist(playlist_name, access_token):
    url = 'https://api.spotify.com/v1/search'
    params = {
        'q': playlist_name,
        'type': 'playlist',
        'limit': 1
    }
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['playlists']['items'][0] if data['playlists']['items'] else None
    else:
        print('Erro ao buscar playlist:', response.status_code)
        return None

def insertPlaylist(playlist):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = """INSERT INTO public.Playlists (id, name, display_name, description, collaborative) VALUES (%s, %s, %s, %s, %s)"""
        val = (playlist['id'], playlist['name'], playlist['owner']['display_name'], playlist['description'], playlist['collaborative'])
        cursor.execute(sql, val)
        connection.commit()
        print(f"Playlist '{playlist['name']}' inserido com sucesso no banco de dados.")
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao inserir a playlist '{playlist['name']}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

# def getPlaylistTracks(playlist_id):
#     try:
#         connection = psycopg2.connect(
#             user=DB_USER,
#             password=DB_PASSWORD,
#             host=DB_HOST,
#             port=DB_PORT,
#             database=DB_NAME
#         )
#         cursor = connection.cursor()
#         sql = """INSERT INTO public.PlaylistTracks (playlist_id, track_id) VALUES (%s, %s)"""
#         val = (playlist_id)
#         cursor.execute(sql, val)
#         playlist = cursor.fetchone()
#         if playlist:
#             return playlist[0]
#         else:
#             return None
#     except (Exception, psycopg2.Error) as error:
#         print(f"Erro ao buscar a playlist '{playlist_name}' no banco de dados:", error)
#     finally:
#         if connection:
#             cursor.close()
#             connection.close()

if __name__ == "__main__":
    filepath = os.path.join('dados', 'playlists.txt')
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            playlist_name = line.strip()
            access_token = getAccessToken(client_id, client_secret)
            playlist_data = getPlaylist(playlist_name, access_token)
            if playlist_data:
                insertPlaylist(playlist_data)
            else:
                print(f"Nenhuma playlist foi encontrado para '{playlist_name}'.")
            # findPlaylist()
