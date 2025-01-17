import os, requests, psycopg2
from dotenv import load_dotenv
from spotify_credentials import client_id, client_secret, getAccessToken

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getGenres(access_token):
    url = 'https://api.spotify.com/v1/recommendations/available-genre-seeds'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        genres = data.get('genres', [])
        return genres
    else:
        print("Erro ao obter gêneros:", response.status_code)
        return []

def insertGenres(genres):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        for genre in genres:
            cursor.execute("INSERT INTO public.Genres (name) VALUES (%s)", (genre,))
        connection.commit()
        print("Gêneros foram inseridos com sucesso no banco de dados.")
    except (Exception, psycopg2.Error) as error:
        print("Erro ao inserir gêneros no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    access_token = getAccessToken(client_id, client_secret)
    genres = getGenres(access_token)
    if genres:
        insertGenres(genres)
    else:
        print("Nenhum gênero foi encontrado.")
