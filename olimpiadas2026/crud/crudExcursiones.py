import psycopg
import os

contraseña = os.getenv("DATABASE_PASSWORD")
dns = f"postgresql://postgres:{contraseña}@db.dncdqfmfixojxprdlbkf.supabase.co:5432/postgres"
conexionViajes = psycopg.connect(dns)
cursor = conexionViajes.cursor()



#Preguntar si la excursiones ya vienen incluidas en el paquete de viaje o hay que comprar.
#No me acuerdo
def agregarExcursiones(excursion_id, nombre, inicio, final, descripcion, lugar):
    cursor.execute("INSERT INTO excursiones (excursion_id, nombre, inicio, final, descripcion, lugar) VALUES(%s,%s,%s,%s,%s,%s)", (excursion_id, nombre, inicio, final, descripcion, lugar))
    conexionViajes.commit()

    return {"Mensaje": "Se ha agregado la excursion exitosamente"}




#28/6 Actualizada, borra primero las relaciones que tiene con pv y luego borra la excursion.
def eliminarExcursion(excursion_id):

    cursor.execute("SELECT * FROM pv_exc WHERE exc_id = %s", (excursion_id,))
    n = cursor.fetchall()
    regExcPvIDs = [] #Guardo los id de las relaciones aca.
    for i in n:
        
        regExcPvIDs.append(i[2])

    for id in regExcPvIDs:
        cursor.execute("DELETE FROM pv_exc WHERE id = %s", (id,))
        conexionViajes.commit()

    cursor.execute("DELETE FROM excursiones WHERE excursion_id = %s", (excursion_id,))
    conexionViajes.commit()

    return {"Mensaje": "Borrado exitosamente"}




#Funcion para enlazar un paquete de viaje con una excursion.
#Primero el id del paquete de viajes despues el id de la excursion.
#Es nueva
def paqueteViajesExcursion(pv_id, exc_id):
    cursor.execute("INSERT INTO pv_exc (pv_id, exc_id) VALUES (%s,%s)", (pv_id, exc_id))
    conexionViajes.commit()

    return {"Mensaje":"Se ha vinculado una excursion con un paquete de viajes"}



#Es nueva(Solo es necesaria por la funcion que esta abajo)
def buscarExcursionporId(excursion_id):
    cursor.execute("SELECT * FROM excursiones WHERE excursion_id = %s", (excursion_id,))
    respuesta = cursor.fetchall()
    dicExcursiones = []
 
    inicio = respuesta[0][2]
    inicio = inicio.strftime("%H:%M:%S")
    final = respuesta[0][3]
    final = final.strftime("%H:%M:%S")

    dicExcursiones.append({

            "Excursion id": respuesta[0][0],
            "Nombre": respuesta[0][1],
            "Inicio": inicio,
            "Final": final,
            "Descripcion": respuesta[0][4],
            "Lugar": respuesta[0][5]
        })
        

    return dicExcursiones

#Esta funcion trae todas las excursiones que el paquete de viajes que se le ingresa
#Es nueva

def verExcursionPaquete(pv_id):
    cursor.execute("SELECT exc_id FROM pv_exc WHERE pv_id = %s", (pv_id,))
    respuesta = cursor.fetchall()
    lista_pv_ids = []
    for excursion in respuesta:
        lista_pv_ids.append(excursion[0])

    excursiones = []
    for i in lista_pv_ids:
        r = buscarExcursionporId(i)
        excursiones.append(r)

    return excursiones


#funcion nueva 16/6 12:12 
def verExcursiones():
    cursor.execute("SELECT * FROM excursiones")
    respuesta = cursor.fetchall()
    excursiones = []

    for exc in respuesta:
        inicio = exc[2]
        inicio = inicio.strftime("%H:%M:%S")
        final = exc[3]
        final = final.strftime("%H:%M:%S")
        excursion = {

            "Excursion id": exc[0],
            "Nombre": exc[1],
            "Inicio": inicio,
            "Final": final,
            "Descripcion": exc[4],
            "Lugar": exc[5]


        }

        excursiones.append(excursion)

    return excursiones




"""print(agregarExcursiones(2, "Excursion a Parque de Diversiones", "8:00", "20:00", "Todo el dia, excursion y dia de familia en los asombrosos juegos del parque de diversion ChasquiBoom.", "ChasquiBoom"))
print(agregarExcursiones(3, "Excursion Lago El Nahuelito", "9:00", "12:00", "Excursion corta, vamos a la hermosa laguna EL Nahuelito, ideal para toda la familia.", "Laguna El Nauelito"))
print(agregarExcursiones(4, "Museo Historico de la Nouvelle Vage", "8:00", "16:00", "Recorrido guiado por el museo de la Nouvelle Vague, durante mañana y tarde.", "Museo Nouvelle Vague"))
print(agregarExcursiones(5, "Reserva Natural Euroean", "8:00", "19:00", "Paseamos por la nueva reserva natural Euroean. Visita guiada y completa.", "Reserva Natural Euroean"))
print(agregarExcursiones(6, "Monumentos y Peculiaridades", "8:00", "13:00", "Tour touristico por la ciudad recorriendo monumenots, esculturas y lugares unicos de la ciudad, charlando con nativos.", "Ciudad"))"""