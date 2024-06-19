import os, requests, psycopg2
from dotenv import load_dotenv
from spotify_credentials import client_id, client_secret, getAccessToken
from shows import findShow

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getEpisodes(show_id, access_token):
    url = f'https://api.spotify.com/v1/shows/{show_id}/episodes'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    limit = 50
    offset = 0
    all_episodes = []
    while True:
        params = {
            'limit': limit,
            'offset': offset,
            'market': 'BR'
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            episodes = data.get('items', [])
            all_episodes.extend(episodes)
            if len(episodes) < limit:
                break
            offset += limit
        else:
            print(f'Erro ao buscar episódios do podcast {show_id}:', response.status_code)
            return None
    return all_episodes

def insertEpisode(show_id, episode):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = """INSERT INTO public.Episodes (id, name, description, duration_ms, release_date, show_id) VALUES (%s, %s, %s, %s, %s, %s)"""
        val = (episode['id'], episode['name'], episode['description'], episode['duration_ms'], episode['release_date'], show_id)
        cursor.execute(sql, val)
        connection.commit()
        print(f"Episódio '{episode['name']}' inserido com sucesso no banco de dados.")
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao inserir o episódio '{episode['name']}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    filepath = os.path.join('dados', 'episodes.txt')
    access_token = getAccessToken(client_id, client_secret)
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            show_id = line.strip()
            show_data = findShow(show_id)
            if show_data:
                episodes = getEpisodes(show_id, access_token)
                if episodes:
                    for episode in episodes:
                        insertEpisode(show_id, episode)
            else:
                print(f"Nenhum audiobook foi encontrado para '{show_data[1]}'.")

