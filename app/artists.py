import os, requests, psycopg2, time
from dotenv import load_dotenv
from spotify_credentials import client_id, client_secret, getAccessToken

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getArtists(artists_id, access_token):
    url = f'https://api.spotify.com/v1/artists?ids={artists_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['artists'] if data['artists'] else None
    else:
        print('Erro ao buscar artistas:', response.status_code)
        return None

def insertArtist(artist):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = """INSERT INTO public.Artists (id, name, genres, followers, popularity) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"""
        val = (artist['id'], artist['name'], artist['genres'], artist['followers']['total'], artist['popularity'])
        cursor.execute(sql, val)
        connection.commit()
        print(f"Artista '{artist['name']}' inserido com sucesso no banco de dados.")
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao inserir o artista '{artist['name']}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

def findArtist(artist_id):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = "SELECT id, name FROM public.Artists WHERE id = %s"
        cursor.execute(sql, (artist_id,))
        artist = cursor.fetchone()
        if artist:
            return artist
        else:
            return None
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao buscar o artista '{artist[1]}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    filepath = os.path.join('dados', 'artists.txt')
    access_token = getAccessToken(client_id, client_secret)
    artist_ids = []
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            artist_id = line.strip()
            if artist_id:
                artist_ids.append(artist_id)
                if len(artist_ids) == 50:
                    artists = getArtists(','.join(artist_ids), access_token)
                    if artists:
                        for artist in artists:
                            insertArtist(artist)
                    else:
                        print("Nenhum artista foi encontrado.")
                    artist_ids = []