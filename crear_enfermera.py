
from getpass import getpass
from werkzeug.security import generate_password_hash
from database import conectar_db

nombre = "Enfermera de Prueba"
correo = "enfermera@sire.test"

contrasena = getpass("Crea una contraseña para SIRE: ")

if not contrasena.strip():
    print("La contraseña no puede estar vacía.")
    raise SystemExit

contrasena_hash = generate_password_hash(contrasena)

conexion = None
cursor = None

try:
    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO enfermeras
        (nombre_completo, correo, contrasena_hash)
        VALUES (%s, %s, %s)
        """,
        (nombre, correo, contrasena_hash)
    )

    conexion.commit()
    print("Cuenta de enfermería creada correctamente.")
    print("Correo:", correo)

except Exception as error:
    if conexion:
        conexion.rollback()
    print("No se pudo crear la cuenta:", error)

finally:
    if cursor:
        cursor.close()
    if conexion:
        conexion.close()
