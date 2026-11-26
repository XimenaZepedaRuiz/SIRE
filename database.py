
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def conectar_db():
    conexion = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        connection_timeout=10,
        charset="utf8mb4"
    )

    return conexion


if __name__ == "__main__":
    try:
        conexion = conectar_db()

        print("Conexion exitosa con MySQL")
        print("Base de datos:", conexion.database)

        conexion.close()

    except mysql.connector.Error as error:
        print("Error de conexion:", error)

    except KeyError as error:
        print("Falta configurar la variable:", error)
