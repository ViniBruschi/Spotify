import os, requests, psycopg2
from dotenv import load_dotenv
from spotify_credentials import client_id, client_secret, getAccessToken
from albums import findAlbum

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getTracks(album_id, access_token):
    url = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['items']
    else:
        print('Erro ao buscar faixas:', response.status_code)
        return None

def insertTrack(album_id, track):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = """INSERT INTO public.Tracks (id, name, duration_ms, album_id, artist_id, track_number) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"""
        val = (track['id'], track['name'], track['duration_ms'], album_id, track['artists'][0]['id'], track['track_number'])
        cursor.execute(sql, val)
        connection.commit()
        print(f"Faixa '{track['name']}' inserido com sucesso no banco de dados.")
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao inserir a faixa '{track['name']}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

def findTrack(track_id):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = "SELECT id FROM public.Tracks WHERE id = %s"
        cursor.execute(sql, (track_id,))
        track = cursor.fetchone()
        if track:
            return track[0]
        else:
            return None
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao buscar a faixa '{track_id}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    filepath = os.path.join('dados', 'tracks.txt')
    access_token = getAccessToken(client_id, client_secret)
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            album_id = line.strip()
            album_data = findAlbum(album_id)
            if album_data:
                print(f"Album {album_data[1]} encontrado no banco de dados.")
                tracks = getTracks(album_id, access_token)
                if tracks:
                    for track in tracks:
                        insertTrack(album_id, track)
                else:
                    print(f"Nenhuma Faixa encontrada para o album '{album_data[1]}'.")
            else:
                print(f"Album '{album_data[1]}' não encontrado no banco de dados.")

