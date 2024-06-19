import os, requests, psycopg2
from dotenv import load_dotenv
from spotify_credentials import client_id, client_secret, getAccessToken

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getShows(show_id, access_token):
    url = f'https://api.spotify.com/v1/shows?ids={show_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'market': 'BR'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['shows'] if data['shows'] else None
    else:
        print('Erro ao buscar Podcasts:', response.status_code)
        return None

def insertShow(show):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = """INSERT INTO public.Shows (id, name, publisher, total_episodes) VALUES (%s, %s, %s, %s)"""
        val = (show['id'], show['name'], show['publisher'], show['total_episodes'])
        cursor.execute(sql, val)
        connection.commit()
        print(f"Podcast '{show['name']}' inserido com sucesso no banco de dados.")
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao inserir o Podcast '{show['name']}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

def findShow(show_id):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = "SELECT id, name FROM public.Shows WHERE id = %s"
        cursor.execute(sql, (show_id,))
        show = cursor.fetchone()
        if show:
            print(f"Podcast '{show[1]}' encontrado no banco de dados")
            return show
        else:
            return None
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao buscar o podcast '{show[1]}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    filepath = os.path.join('dados', 'shows.txt')
    access_token = getAccessToken(client_id, client_secret)
    shows_ids = []
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            show_id = line.strip()
            if show_id:
                shows_ids.append(show_id)
                if len(shows_ids) == 50:
                    shows = getShows(','.join(shows_ids), access_token)
                    if shows:
                        for show in shows:
                            insertShow(show)
                    else:
                        print("Nenhum podcast foi encontrado.")
                    shows_ids = []