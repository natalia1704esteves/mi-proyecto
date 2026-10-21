import psycopg2

sql_crear_tabla_pacientes = """
CREATE TABLE IF NOT EXISTS pacientes (
    id SERIAL PRIMARY KEY,
    cedula VARCHAR(15) UNIQUE NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

try:
    # Agregamos client_encoding para evitar el error de caracteres/tildes
    conexion = psycopg2.connect(
        host="localhost",
        database="sigep",
        user="postgres",
        password="solano",  # Reemplaza por tu clave real
        port="5432",
        client_encoding="utf8"
    )

    cursor = conexion.cursor()
    cursor.execute(sql_crear_tabla_pacientes)
    conexion.commit()

    print("-----------------------------------------")
    print("¡Tabla 'pacientes' creada exitosamente!")
    print("-----------------------------------------")

    cursor.close()
    conexion.close()

except Exception as error:
    print("-----------------------------------------")
    print(f"Error al intentar conectar: {error}")
    print("-----------------------------------------")