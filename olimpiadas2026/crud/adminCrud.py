import psycopg
import os

DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
dns = f"postgresql://postgres.dncdqfmfixojxprdlbkf:{DATABASE_PASSWORD}@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
conexionViajes = psycopg.connect(dns) 
cursor = conexionViajes.cursor()

def crearAdminsitradores(ua_id, nombre, apellido, contraseña, correo_electronico):
    cursor.execute("INSERT INTO usuario_administrativo (ua_id, nombre, apellido, contraseña, correo_electronico) VALUES(%s,%s,%s,%s,%s)", (ua_id, nombre, apellido, contraseña, correo_electronico))
    conexionViajes.commit()
    
    return {"Mensaje":"Se ha creado un nuevo administrador"}


def borrarAdmin(ua_id):
    cursor.execute("DELETE FROM usuario_administrativo WHERE ua_id = %s",(ua_id,))
    conexionViajes.commit()

    return {"Mensaje": "Se ha eliminado un administrador"}


