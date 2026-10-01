"""Agregar un catálogo de demostración sin reemplazar registros existentes.
Ejecutar desde backend: .venv/bin/python seed_demo.py
"""
from datetime import date, timedelta, time
from main import get_connection


def seed():
    added = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('LOCK TABLE viaje_simple, paquete_de_viajes, auto, excursiones, vs_at, exc_at, pv_exc IN SHARE ROW EXCLUSIVE MODE')
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
            for dest,model,price in [('Bariloche','SUV compacta',62000),('Mendoza','Sedán',45000),('Iguazú','Compacto',38000),('Mar del Plata','Familiar',55000)]:
                model=f'DEMO - {model} ({dest})'
                cur.execute('SELECT auto_id FROM auto WHERE modelo=%s',(model,))
                row=cur.fetchone()
                if row: auto_id=row[0]
                else:
                    cur.execute('SELECT COALESCE(MAX(auto_id),0)+1 FROM auto'); auto_id=cur.fetchone()[0]
                    cur.execute('INSERT INTO auto(auto_id,modelo,disponibles,precio_por_dia) VALUES(%s,%s,5,%s)',(auto_id,model,price)); added+=1
                # Los vínculos no se duplican y no se restauran artículos archivados.
                cur.execute("SELECT codigo FROM viaje_simple WHERE destino=%s AND eliminado_en IS NULL AND nombre LIKE 'DEMO -%%'",(dest,))
                for (trip_id,) in cur.fetchall():
                    cur.execute('INSERT INTO vs_at(id,vs_id,at_id) SELECT (SELECT COALESCE(MAX(id),0)+1 FROM vs_at),%s,%s WHERE NOT EXISTS(SELECT 1 FROM vs_at WHERE vs_id=%s AND at_id=%s)',(trip_id,auto_id,trip_id,auto_id))
                cur.execute("SELECT codigo FROM paquete_de_viajes WHERE destino=%s AND eliminado_en IS NULL AND nombre LIKE 'DEMO -%%'",(dest,))
                for (package_id,) in cur.fetchall():
                    cur.execute('INSERT INTO exc_at(id,pv_id,at_id) SELECT (SELECT COALESCE(MAX(id),0)+1 FROM exc_at),%s,%s WHERE NOT EXISTS(SELECT 1 FROM exc_at WHERE pv_id=%s AND at_id=%s)',(package_id,auto_id,package_id,auto_id))
            for dest,title in [('Bariloche','Circuito Chico'),('Mendoza','Visita a bodegas'),('Iguazú','Paseo por cataratas')]:
                name=f'DEMO - {title}'
                cur.execute('SELECT excursion_id FROM excursiones WHERE nombre=%s',(name,)); row=cur.fetchone()
                if row: excursion_id=row[0]
                else:
                    cur.execute('SELECT COALESCE(MAX(excursion_id),0)+1 FROM excursiones'); excursion_id=cur.fetchone()[0]
                    cur.execute('INSERT INTO excursiones(excursion_id,nombre,inicio,final,descripcion,lugar) VALUES(%s,%s,%s,%s,%s,%s)',(excursion_id,name,time(9),time(13),'Actividad ficticia para demostración; no es una reserva real.',dest)); added+=1
                cur.execute("SELECT codigo FROM paquete_de_viajes WHERE destino=%s AND eliminado_en IS NULL AND nombre LIKE 'DEMO -%%'",(dest,))
                for (package_id,) in cur.fetchall():
                    cur.execute('INSERT INTO pv_exc(id,pv_id,exc_id) SELECT (SELECT COALESCE(MAX(id),0)+1 FROM pv_exc),%s,%s WHERE NOT EXISTS(SELECT 1 FROM pv_exc WHERE pv_id=%s AND exc_id=%s)',(package_id,excursion_id,package_id,excursion_id))
    print(f'Registros de demostración agregados: {added}')


if __name__ == '__main__':
    seed()
