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
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['items']
    else:
        print('Erro ao buscar episódios:', response.status_code)
        return None

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
    filepath = os.path.join('dados', 'shows.txt')
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            show_name = line.strip()
            access_token = getAccessToken(client_id, client_secret)
            show_data = findShow(show_name)
            if show_data:
                print(f"Podcast encontrado no banco de dados.")
                episodes = getEpisodes(show_data, access_token)
                if episodes:
                    for episode in episodes:
                        insertEpisode(show_data, episode)
                else:
                    print(f"Nenhum Episódio encontrado para o Podcast '{show_name}'.")
            else:
                print(f"Podcast '{show_name}' não encontrado no banco de dados.")

