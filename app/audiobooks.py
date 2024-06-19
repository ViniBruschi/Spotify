import os, requests, psycopg2
from dotenv import load_dotenv
from spotify_credentials import client_id, client_secret, getAccessToken

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getAudiobooks(audiobook_id, access_token):
    url = f'https://api.spotify.com/v1/audiobooks?ids={audiobook_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'market': 'US'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['audiobooks'] if data['audiobooks'] else None
    else:
        print('Erro ao buscar audiobooks:', response.status_code)
        return None

def insertAudiobook(audiobook):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = """INSERT INTO public.Audiobooks (id, name, authors, narrators, publisher, total_chapters) VALUES (%s, %s, %s, %s, %s, %s)"""
        authors = [author['name'] for author in audiobook['authors']]
        narrators = [narrator['name'] for narrator in audiobook['narrators']]
        val = (audiobook['id'], audiobook['name'], authors, narrators, audiobook['publisher'], audiobook['total_chapters'])
        cursor.execute(sql, val)
        connection.commit()
        print(f"Audiobook '{audiobook['name']}' inserido com sucesso no banco de dados.")
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao inserir o Audiobook '{audiobook['name']}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

def findAudiobook(audiobook_id):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        sql = "SELECT id, name FROM public.Audiobooks WHERE id = %s"
        cursor.execute(sql, (audiobook_id,))
        audiobook = cursor.fetchone()
        if audiobook:
            print(f"Audiobook '{audiobook[1]}' encontrado no banco de dados")
            return audiobook
        else:
            return None
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao buscar o audiobook '{audiobook[1]}' no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            
if __name__ == "__main__":
    filepath = os.path.join('dados', 'audiobooks.txt')
    access_token = getAccessToken(client_id, client_secret)
    audiobooks_ids = []
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            audiobook_id = line.strip()
            if audiobook_id:
                audiobooks_ids.append(audiobook_id)
                if len(audiobooks_ids) == 50:
                    audiobooks = getAudiobooks(','.join(audiobooks_ids), access_token)
                    if audiobooks:
                        for audiobook in audiobooks:
                            insertAudiobook(audiobook)
                    else:
                        print("Nenhum audiobook foi encontrado.")
                    audiobooks_ids = []