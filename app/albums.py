import os, requests, psycopg2
from dotenv import load_dotenv
from spotify_credentials import client_id, client_secret, getAccessToken
from artists import findArtist

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getAlbums(artist_id, access_token):
    url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'
    params = {
        'type': 'album',
        'limit': 50
    }
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['items']
    else:
        print('Erro ao buscar albums:', response.status_code)
        return None

def insertAlbum(album):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = """INSERT INTO public.Albums (id, name, release_date, total_tracks, artist_id, album_type) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"""
        val = (album['id'], album['name'], album['release_date'], album['total_tracks'], album['artists'][0]['id'], album['type'])
        cursor.execute(sql, val)
        connection.commit()
        print(f"Album '{album['name']}' inserido com sucesso no banco de dados.")
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao inserir o album '{album['name']}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

def findAlbum(album_name):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = "SELECT id FROM public.Albums WHERE name ILIKE %s"
        cursor.execute(sql, ('%' + album_name + '%',))
        album = cursor.fetchone()
        if album:
            return album[0]
        else:
            return None
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao buscar o album '{album_name}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    filepath = os.path.join('dados', 'albums.txt')
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            artist_name = line.strip()
            access_token = getAccessToken(client_id, client_secret)
            artist_data = findArtist(artist_name)
            if artist_data:
                print(f"Artista encontrado no banco de dados.")
                albums = getAlbums(artist_data, access_token)
                if albums:
                    for album in albums:
                        insertAlbum(album)
                else:
                    print(f"Nenhum Album encontrado para o artista '{artist_name}'.")
            else:
                print(f"Artista '{artist_name}' não encontrado no banco de dados.")

