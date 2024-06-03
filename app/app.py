import os
import psycopg2

def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        print("Conexão ao banco de dados estabelecida com sucesso!")
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)
        return None

def close_connection(conn):
    try:
        if conn is not None:
            conn.close()
            print("Conexão ao banco de dados fechada.")
    except Exception as e:
        print("Erro ao fechar a conexão com o banco de dados:", e)

if __name__ == "__main__":
    connection = connect_to_database()
    close_connection(connection)
