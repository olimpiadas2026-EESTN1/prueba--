import psycopg
import os

contraseña = os.getenv("DATABASE_PASSWORD")
dns = f"postgresql://postgres:{contraseña}@db.dncdqfmfixojxprdlbkf.supabase.co:5432/postgres"
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


