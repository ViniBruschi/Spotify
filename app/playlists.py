import os
import requests
import psycopg2
from dotenv import load_dotenv
from spotify_credentials import client_id, client_secret, getAccessToken
from tracks import findTrack

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getPlaylist(playlist_id, access_token):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
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
        sql = """INSERT INTO public.Playlists (id, name, display_name, description, collaborative, user_id) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"""
        val = (playlist['id'], playlist['name'], playlist['owner']['display_name'], playlist['description'], playlist['collaborative'], playlist['owner']['id'])
        cursor.execute(sql, val)
        connection.commit()
        print(f"Playlist '{playlist['name']}' inserido com sucesso no banco de dados.")
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao inserir a playlist '{playlist['name']}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

def getPlaylistTracks(playlist_id, access_token):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    limit = 50
    offset = 0
    all_tracks = []

    while True:
        params = {
            'limit': limit,
            'offset': offset
        }
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            tracks = data.get('items', [])
            all_tracks.extend(tracks)
            if len(tracks) < limit:
                break
            offset += limit
        else:
            print(f'Erro ao buscar faixas da playlist {playlist_id}:', response.status_code)
            return None

    return all_tracks

def insertPlaylistTrack(playlist_id, track_id):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = """INSERT INTO public.PlaylistTracks (playlist_id, track_id) VALUES (%s, %s) ON CONFLICT DO NOTHING"""
        val = (playlist_id, track_id)
        cursor.execute(sql, val)
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao inserir a faixa '{track_id}' da playlist '{playlist_id}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    filepath = os.path.join('dados', 'playlists.txt')
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            playlist_id = line.strip()
            access_token = getAccessToken(client_id, client_secret)
            playlist_data = getPlaylist(playlist_id, access_token)
            if playlist_data:
                insertPlaylist(playlist_data)
                tracks = getPlaylistTracks(playlist_id, access_token)
                if tracks:
                    for track_item in tracks:
                        track = track_item['track']
                        track_id = findTrack(track['id'])
                        if track_id:
                            insertPlaylistTrack(playlist_data['id'], track['id'])
                        else:
                            print(f"Faixa {track['name']} não encontrada no banco de dados")
            else:
                print(f"Nenhuma playlist foi encontrada para '{playlist_id}'.")
