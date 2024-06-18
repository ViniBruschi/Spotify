import os, requests, psycopg2
from dotenv import load_dotenv
from spotify_credentials import client_id, client_secret, getAccessToken

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getShow(show_name, access_token):
    url = 'https://api.spotify.com/v1/search'
    params = {
        'q': show_name,
        'type': 'show',
        'limit': 1,
        'market': 'BR'
    }
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['shows']['items'][0] if data['shows']['items'] else None
    else:
        print('Erro ao buscar podcast:', response.status_code)
        return None

def insertShows(show):
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

def findShow(show_name):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = "SELECT id FROM public.Shows WHERE name ILIKE %s"
        cursor.execute(sql, ('%' + show_name + '%',))
        show = cursor.fetchone()
        if show:
            return show[0]
        else:
            return None
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao buscar o podcast '{show_name}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    filepath = os.path.join('dados', 'shows.txt')
    with open(filepath, 'r', encoding='utf-8') as file:
        access_token = getAccessToken(client_id, client_secret)
        for line in file:
            show_name = line.strip()
            show_data = getShow(show_name, access_token)
            if show_data:
                insertShows(show_data)
            else:
                print(f"Nenhum podcast foi encontrado para '{show_name}'.")
