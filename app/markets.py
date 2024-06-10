import os
from dotenv import load_dotenv
import requests
from spotify_credentials import client_id, client_secret, getAccessToken
import psycopg2

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def getMarkets(access_token):
    markets_url = 'https://api.spotify.com/v1/markets'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(markets_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        markets = data.get('markets', [])
        return markets
    else:
        print("Erro ao obter mercados:", response.status_code)
        return []

def insertMarkets(markets):
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = connection.cursor()
        for market in markets:
            cursor.execute("INSERT INTO public.Markets (country) VALUES (%s)", (market,))
        connection.commit()
        print("Mercados foram inseridos no banco de dados com sucesso!")
    except (Exception, psycopg2.Error) as error:
        print("Erro ao inserir Mercados no banco de dados:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    access_token = getAccessToken(client_id, client_secret)
    genres = getMarkets(access_token)
    if genres:
        insertMarkets(genres)
    else:
        print("Nenhum Mercado foi encontrado.")
