import os, requests, psycopg2
from dotenv import load_dotenv
from spotify_credentials import client_id, client_secret, getAccessToken

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getAudiobook(audiobook_name, access_token):
    url = 'https://api.spotify.com/v1/search'
    params = {
        'q': audiobook_name,
        'type': 'audiobook',
        'limit': 1,
        'market': 'US'
    }
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['audiobooks']['items'][0] if data['audiobooks']['items'] else None
    else:
        print('Erro ao buscar audiobook:', response.status_code)
        return None

def insertAudiobooks(audiobook):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        print(audiobook)
        sql = """INSERT INTO public.Audiobooks (id, name, authors, narrators, publisher, total_chapters) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        val = (audiobook['id'], audiobook['name'], audiobook['authors'], audiobook['narrators'], audiobook['publisher'], audiobook['total_chapters'])
        cursor.execute(sql, val)
        connection.commit()
        print(f"Audiobook '{audiobook['name']}' inserido com sucesso no banco de dados.")
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao inserir o Audiobook '{audiobook['name']}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

def findShow(audiobook_name):
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
        cursor.execute(sql, ('%' + audiobook_name + '%',))
        audiobook = cursor.fetchone()
        if audiobook:
            return audiobook[0]
        else:
            return None
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao buscar o podcast '{audiobook_name}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    filepath = os.path.join('dados', 'audiobooks.txt')
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            audiobook_name = line.strip()
            access_token = getAccessToken(client_id, client_secret)
            audiobook_data = getAudiobook(audiobook_name, access_token)
            if audiobook_data:
                insertAudiobooks(audiobook_data)
            else:
                print(f"Nenhum audiobook foi encontrado para '{audiobook_name}'.")
