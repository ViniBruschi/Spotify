import os, requests, psycopg2
from dotenv import load_dotenv
from spotify_credentials import client_id, client_secret, getAccessToken

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getArtist(artist_name, access_token):
    url = 'https://api.spotify.com/v1/search'
    params = {
        'q': artist_name,
        'type': 'artist',
        'limit': 1
    }
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['artists']['items'][0] if data['artists']['items'] else None
    else:
        print('Erro ao buscar artista:', response.status_code)
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

def findArtist(artist_name):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = "SELECT id FROM public.Artists WHERE name ILIKE %s"
        cursor.execute(sql, ('%' + artist_name + '%',))
        artist = cursor.fetchone()
        if artist:
            return artist[0]
        else:
            return None
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao buscar o artista '{artist_name}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    filepath = os.path.join('dados', 'artists.txt')
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            artist_name = line.strip()
            access_token = getAccessToken(client_id, client_secret)
            artist_data = getArtist(artist_name, access_token)
            if artist_data:
                insertArtist(artist_data)
            else:
                print(f"Nenhum artista foi encontrado para '{artist_name}'.")
