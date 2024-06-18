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
    limit = 50
    offset = 0
    all_categories = []
    response = requests.get(url, headers=headers)
    while True:
        params = {
            'limit': limit,
            'offset': offset
        }
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            categories = data.get('categories', {}).get('items', [])
            all_categories.extend(categories)
            if len(categories) < limit:
                break
            offset += limit
        else:
            print(f'Erro ao buscar categorias:', response.status_code)
            return None

    return all_categories

def insertCategories(category):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO public.Categories (id, name) VALUES (%s, %s)",
            (category['id'], category['name'])
        )
        connection.commit()
        print(f"Categoria {category['name']} foi inserida no banco de dados!")
    except (Exception, psycopg2.Error) as error:
        print(f"Erro ao inserir categoria {category['name']} no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    access_token = getAccessToken(client_id, client_secret)
    categories = getCategories(access_token)
    if categories:
        for category in categories:
            insertCategories(category)
    else:
        print("Nenhuma categoria foi encontrada.")
