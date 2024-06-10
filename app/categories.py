import os, requests, psycopg2
from dotenv import load_dotenv
from spotify_credentials import client_id, client_secret, getAccessToken

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getCategories(access_token):
    url = 'https://api.spotify.com/v1/browse/categories'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        categories = data.get('categories', {}).get('items', [])
        return categories, data
    else:
        print("Erro ao obter categorias:", response.status_code)
        return [], {}

def insertCategories(categories):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        for category in categories:
            cursor.execute(
                "INSERT INTO public.Categories (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
                (category['id'], category['name'])
            )
        connection.commit()
        print("Categorias foram inseridas no banco de dados com sucesso!")
    except (Exception, psycopg2.Error) as error:
        print("Erro ao inserir categorias no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    access_token = getAccessToken(client_id, client_secret)
    categories, categories_json = getCategories(access_token)
    if categories:
        insertCategories(categories)
    else:
        print("Nenhuma categoria foi encontrada.")
