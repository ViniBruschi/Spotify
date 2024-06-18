import os, requests, psycopg2
from dotenv import load_dotenv
from datetime import datetime
from spotify_credentials import client_id, client_secret, getAccessToken
from audiobooks import findAudiobook

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getChapters(audiobook_id, access_token):
    url = f'https://api.spotify.com/v1/audiobooks/{audiobook_id}/chapters'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    limit = 50
    offset = 0
    all_chapters = []

    while True:
        params = {
            'limit': limit,
            'offset': offset,
            'market': 'US'
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            chapters = data.get('items', [])
            all_chapters.extend(chapters)
            if len(chapters) < limit:
                break
            offset += limit
        else:
            print(f'Erro ao buscar capítulos do audiobook {audiobook_id}:', response.status_code)
            return None
    return all_chapters

def insertChapter(audiobook_id, chapter):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        release_date = chapter['release_date']
        precision = chapter['release_date_precision']
        if release_date != "0000":
            if precision == 'year':
                release_date = datetime.strptime(release_date, '%Y').date().replace(month=1, day=1)
            elif precision == 'month':
                release_date = datetime.strptime(release_date, '%Y-%m').date().replace(day=1)
            else:
                release_date = datetime.strptime(release_date, '%Y-%m-%d').date()
        else:
            release_date = None

        cursor = connection.cursor()
        sql = """INSERT INTO public.Chapters (id, name, chapter_number, duration_ms, release_date, audiobook_id) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"""
        val = (chapter['id'], chapter['name'], chapter['chapter_number'], chapter['duration_ms'], release_date, audiobook_id)
        cursor.execute(sql, val)
        connection.commit()
        print(f"Capítulo '{chapter['name']}' inserido com sucesso no banco de dados.")
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao inserir o capítulo '{chapter['name']}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    filepath = os.path.join('dados', 'chapters.txt')
    with open(filepath, 'r', encoding='utf-8') as file:
        access_token = getAccessToken(client_id, client_secret)
        for line in file:
            audiobook_name = line.strip()
            audiobook_id = findAudiobook(audiobook_name)
            if audiobook_id:
                chapters = getChapters(audiobook_id, access_token)
                if chapters:
                    for chapter in chapters:
                        insertChapter(audiobook_id, chapter)
            else:
                print(f"Nenhum audiobook foi encontrado para '{audiobook_name}'.")