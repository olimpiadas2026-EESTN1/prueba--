#La tabla que maneja este crud es Ventas
import psycopg
from crudViajes import convertirDate, convertirHora, restarCupoTPV, restarCupoTVS,consultarCuposTPV,consultarCuposTVS
import os

contraseña = os.getenv("DATABASE_PASSWORD")
dns = f"postgresql://postgres:{contraseña}@db.dncdqfmfixojxprdlbkf.supabase.co:5432/postgres"
conexionViajes = psycopg.connect(dns)
cursor = conexionViajes.cursor()


def convertirDatosVentas(respuesta):
    
    registros = []
    for registro in respuesta:
        dicConvertido = []
        fecha = registro[1]
        fecha = fecha.strftime("%Y-%m-%d")
        hora = registro[2]
        hora = hora.strftime("%H:%M:%S")

        if(registro[6]):#Si no esta vacia quiere decir que la venta es de un viaje simple(revisar orden de campos en la tabla clientes)
            codigo_de_viaje = registro[6]
            tipo = "Viaje Simple"
        else:#Si item[6] esta vacio quiere decir que es un paquete de viaje(revisar orden de capos en la taba cliente)
            codigo_de_viaje = registro[7]
            tipo = "Paquete de Viaje"
        #Consultar si es necesario agregar a la tabla venta un campo que indique si la venta es de un paquete de viajes o de un viaje simple
        dicConvertido.append({

                            "Id Venta": registro[0],
                             "Fecha": fecha,
                             "Hora": hora,
                             "Medio de pago": registro[3],
                             "Cuotas": registro[4], 
                             "Cantidad": registro[5], 
                             "Codigo de viaje": codigo_de_viaje, 
                             "Tipo": tipo, 
                             "Precio": registro[8]})
        registros.append(dicConvertido)

    return registros

def verVentas():
    #En la tabla Ventas
 
    cursor.execute("SELECT * FROM ventas")
    respuesta = cursor.fetchall()
    nrespuesta = convertirDatosVentas(respuesta)
    

    return nrespuesta

#Modificada otra vez 22:58hrs!!! importante!!!
def sumarVenta(vtas_id, fecha, hora, medio_de_pago, cuotas, cantidad, codigo_vs, codigo_pv, precio, uc_id):#Agregue usuario id

        fecha = convertirDate(fecha)
        hora = convertirHora(hora)
        cursor.execute("INSERT INTO ventas (vtas_id, fecha, hora, medio_de_pago, cuotas, cantidad, codigo_vs, codigo_pv, precio) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", (vtas_id, fecha, hora, medio_de_pago, cuotas, cantidad,codigo_vs, codigo_pv, precio))
        cursor.execute("INSERT INTO vtas_uc (vtas_id, uc_id) VALUES(%s,%s)",(vtas_id,uc_id))
        conexionViajes.commit()#Dejar elcommit() aca !!!!!
        if(codigo_vs):
            #Consultar cupos es por si llegara a 0 y hay que marcarle no disponible
            restarCupoTVS(codigo_vs, cantidad)
            consultarCuposTVS(codigo_vs)
            
        else:
            #Consultar cupos es por si llegara a 0 y hay que marcarle no disponible
            restarCupoTPV(codigo_pv, cantidad)
            consultarCuposTPV(codigo_pv)
            

        
        return {"Mensaje":"Venta sumada"}

        

def buscarVentaId(vtas_id):

    cursor.execute("SELECT * FROM ventas WHERE vtas_id = %s", (vtas_id,))
    registro = cursor.fetchall()
    dicConvertido = []
    fecha = registro[0][1]
    fecha = fecha.strftime("%Y-%m-%d")
    hora = registro[0][2]
    hora = hora.strftime("%H:%M:%S")


    if(registro[0][6]):#Si no esta vacia quiere decir que la venta es de un viaje simple(revisar orden de campos en la tabla clientes)
            codigo_de_viaje = registro[0][6]
            tipo = "Viaje Simple"
    else:#Si item[6] esta vacio quiere decir que es un paquete de viaje(revisar orden de capos en la taba cliente)
            codigo_de_viaje = registro[0][7]
            tipo = "Paquete de Viaje"


    dicConvertido.append({

                            "Id Venta": registro[0][0],
                             "Fecha": fecha,
                             "Hora": hora,
                             "Medio de pago": registro[0][3],
                             "Cuotas": registro[0][4], 
                             "Cantidad": registro[0][5], 
                             "Codigo de viaje": codigo_de_viaje, 
                             "Tipo": tipo, 
                             "Precio": registro[0][8]})

    return dicConvertido


#Anda, es nueva 23:43hrs
def cancelarCompraTVS(vtas_id):
    venta = buscarVentaId(vtas_id)
    cantidad = venta[0]["Cantidad"]
    codigoViaje = venta[0]["Codigo de viaje"]

    cursor.execute("UPDATE viaje_simple SET cupos = cupos + %s WHERE codigo = %s",(cantidad, codigoViaje))
    cursor.execute("DELETE FROM vtas_uc WHERE vtas_id = %s", (vtas_id,))
    cursor.execute("DELETE FROM ventas WHERE vtas_id = %s",(vtas_id,))

    conexionViajes.commit()



    return {"Mensaje":"Compra cancelada"}


#Anda, es nueva 23:43hrs
def cancelarCompraTPV(vtas_id):
    venta = buscarVentaId(vtas_id)
    cantidad = venta[0]["Cantidad"]
    codigoViaje = venta[0]["Codigo de viaje"]

    cursor.execute("UPDATE paquete_de_viajes SET cupos = cupos + %s WHERE codigo = %s",(cantidad, codigoViaje))
    cursor.execute("DELETE FROM vtas_uc WHERE vtas_id = %s", (vtas_id,))
    cursor.execute("DELETE FROM ventas WHERE vtas_id = %s",(vtas_id,))

    conexionViajes.commit()



    return {"Mensaje":"Compra cancelada"}


#print(cancelarCompraTPV(1000))



"""print(sumarVenta(2,"14/11/25","9:11","Transferncia", True, 1, None, 715, 10000))
print(sumarVenta(3,"21/12/25","21:15","Transferncia", False, 1, None, 2455, 70000))
print(sumarVenta(4,"20/1/25","20:13","Transferncia", True, 1, 679848, None, 27000))"""


    




