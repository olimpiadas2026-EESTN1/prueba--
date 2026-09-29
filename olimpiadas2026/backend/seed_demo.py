"""Agregar un catálogo de demostración sin reemplazar registros existentes.
Ejecutar desde backend: .venv/bin/python seed_demo.py
"""
from datetime import date, timedelta, time
import psycopg
from main import hostURL


def seed():
    added = 0
    with psycopg.connect(hostURL, connect_timeout=10) as conn:
        with conn.cursor() as cur:
            cur.execute('LOCK TABLE viaje_simple, paquete_de_viajes IN SHARE ROW EXCLUSIVE MODE')
            trips = [
                ('Bariloche', 'Avion', 185000, '2 h 20 min'),
                ('Mendoza', 'Avion', 125000, '1 h 50 min'),
                ('Iguazú', 'Avion', 160000, '1 h 45 min'),
                ('Mar del Plata', 'Micro', 45000, '5 horas'),
                ('Córdoba', 'Micro', 65000, '9 horas'),
                ('Rosario', 'Micro', 38000, '4 horas'),
            ]
            for index, (dest, transport, price, duration) in enumerate(trips):
                name = f'DEMO - {dest} en {transport}'
                cur.execute('SELECT 1 FROM viaje_simple WHERE nombre = %s', (name,))
                if cur.fetchone():
                    continue
                cur.execute('SELECT COALESCE(MAX(codigo), 0) + 1 FROM viaje_simple')
                code = cur.fetchone()[0]
                cur.execute('''INSERT INTO viaje_simple
                    (codigo,nombre,descripcion,precio,origen,destino,transporte,fecha,hora,cupos,duracion_aprox,tipo_de_viaje,estado)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                    (code,name,'Demostración: itinerario y precio ficticios para probar el sitio.',price,
                     'Buenos Aires',dest,transport,date.today()+timedelta(days=30+index*3),time(10,30),25,duration,'solo ida','Disponible'))
                added += 1
            for index, (dest, price, nights) in enumerate([('Bariloche',420000,5),('Mendoza',280000,3),('Iguazú',350000,4)]):
                name = f'DEMO - Escapada a {dest}'
                cur.execute('SELECT 1 FROM paquete_de_viajes WHERE nombre = %s', (name,))
                if cur.fetchone():
                    continue
                cur.execute('SELECT COALESCE(MAX(codigo), 0) + 1 FROM paquete_de_viajes')
                code = cur.fetchone()[0]
                cur.execute('''INSERT INTO paquete_de_viajes
                    (codigo,nombre,precio,origen,destino,estadia,tipo,descripcion,cupos,duracion,tipo_de_viaje,hora,fecha,estado)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                    (code,name,price,'Buenos Aires',dest,f'{nights} noches','ida y vuelta',
                     'Demostración: paquete y precio ficticios para probar el sitio.',15,f'{nights+1} días',
                     'Nacional',time(9),date.today()+timedelta(days=45+index*4),'Disponible'))
                added += 1
    print(f'Registros de demostración agregados: {added}')


if __name__ == '__main__':
    seed()
