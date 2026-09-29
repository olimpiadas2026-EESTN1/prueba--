import psycopg
import os

DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
dns = f"postgresql://postgres.dncdqfmfixojxprdlbkf:{DATABASE_PASSWORD}@aws-0-us-west-2.pooler.supabase.com:5432/postgres"
conexionViajes = psycopg.connect(dns)
cursor = conexionViajes.cursor()


def agregarAuto(auto_id, modelo, disponibles, precio_por_dia):
    cursor.execute("INSERT INTO auto (auto_id, modelo, disponibles, precio_por_dia) VALUES(%s,%s,%s,%s)", (auto_id, modelo, disponibles, precio_por_dia))
    conexionViajes.commit()

    return {"mensaje":"Nuevo auto cargado exitosamente"}





#Tambien modificado para que se borren las relaciones vs-auto pv-auto y luego se elimine.
def borrarAuto(auto_id):

    cursor.execute("SELECT id FROM vs_at WHERE at_id = %s", (auto_id,))
    r = cursor.fetchall()
    regAtVsIdDs = []
    for i in r:
        regAtVsIdDs.append(i[0])

    for registroId in regAtVsIdDs:
        cursor.execute("DELETE FROM vs_at WHERE id = %s", (registroId,))
        conexionViajes.commit()

    cursor.execute("SELECT id FROM exc_at WHERE at_id = %s", (auto_id,))
    n = cursor.fetchall()
    regAtPVIdDs = []
    for i in n:
        regAtPVIdDs.append(i[0])
        
    for registroId in regAtPVIdDs:
        cursor.execute("DELETE FROM exc_at WHERE id = %s", (registroId,))
        conexionViajes.commit()


    cursor.execute("DELETE FROM auto WHERE auto_id = %s",(auto_id,))
    conexionViajes.commit()
    
    return {"Mensaje":"Auto eliminado exitosamente"}



#Dos funciones: una para vincular un paquete de viajes a un auto y otra para vincular un viaje simple a un auto.

def vinculaVSaAuto(vs_id, at_id):
    #vs_id el viaje simple al que se le va a asignar un auto
    #at_Id el auto al que se le va a asignar un viaje simple

    cursor.execute("INSERT INTO vs_at (vs_id, at_id) VALUES(%s,%s)",(vs_id, at_id))
    conexionViajes.commit()

    return {"Mensaje": "Se ha asignado un auto a un viaje simple"}

def vincularPVaAuto(pv_id, at_id):
    #pv_id el codigo de paquete de viajes
    #at_id el id del auto
    cursor.execute("INSERT INTO exc_at (pv_id, at_id) VALUES(%s,%s)",(pv_id, at_id))

    return {"Mensaje": "Se ha asignado un auto a un paquete de viajes"}





def verAutoID(auto_id):
    cursor.execute("SELECT * FROM auto WHERE auto_Id = %s", (auto_id,))
    respuesta = cursor.fetchall()
    respuesta  = {
        "auto id": respuesta[0][0],
        "modelo": respuesta[0][1],
        "disponibles": respuesta[0][2],
        "precio por dia": respuesta[0][3]
    }    

    

    return respuesta





#Listo, nueva anda
def verAutoPV(pv_id):
    cursor.execute("SELECT * FROM exc_at WHERE pv_id = %s", (pv_id,))
    respuesta = cursor.fetchall()
    lista = []
    dicAutos = []
    for i in respuesta:
        lista.append(i[1])
    for n in lista:
        
        dicAutos.append(verAutoID(n))
    
    return dicAutos


#print(verAutoPV(2455))

"""cursor.execute("SELECT * FROM exc_at WHERE pv_id = %s", (755,))
respuesta = cursor.fetchall()
lista = []
dicAutos = []
for i in respuesta:
    print(i[1])
    lista.append(i[1])
for n in lista:
    print(verAutoID(n))
    dicAutos.append(verAutoID(n))"""




#print(verAutoPV(755))
#print(respuesta)

#Listo, es nueva anda
def verAutoVs(vs_id):
    cursor.execute("SELECT * FROM vs_at WHERE vs_id = %s", (vs_id,))
    respuesta = cursor.fetchall()
    autos = []
    autoInfo = []
    for i in respuesta[0]:
        autos.append(respuesta[1][1])
    for auto in autos:
        r = verAutoID(auto)
        autoInfo.append(r)
    
    return autoInfo



#FUNCION NUEVA 16/6 12:05 importante

def verAutos():
    cursor.execute("SELECT *  FROM auto")
    respuesta = cursor.fetchall()
    autos = []
    for auto in respuesta:
        at = {
        "auto id": auto[0],
        "modelo": auto[1],
        "disponibles": auto[2],
        "precio por dia": auto[3]

        }  

        autos.append(at) 


    return autos


##print(verAutos())
    


