"""Comprobación de lectura del backend real, sin crear compras ni enviar correos.
Ejecutar desde backend: .venv/bin/python verificar_catalogo.py
Los permisos administrativos se sustituyen solo dentro del cliente de pruebas.
No expone usuarios, contraseñas ni tokens en la salida.
"""
from fastapi.testclient import TestClient
import main
from modulos.administradores import require_admin

def verificar():
    client=TestClient(main.app)
    paths=['/health','/viajes/obtener','/paqueteDeViajes/obtener','/autos/obtener','/excursiones/obtener']
    payloads={}
    def check(method,path,body=None,expected=200):
        r=client.request(method,path,json=body);d=r.json()
        assert r.status_code==expected,(path,r.status_code)
        if expected==200: assert not isinstance(d,dict) or 'error' not in d,path
        print(path,r.status_code,'registros='+str(len(d)) if isinstance(d,list) else 'OK')
        return d
    for path in paths:payloads[path]=check('GET',path)
    trips=payloads['/viajes/obtener'];packages=[p for group in payloads['/paqueteDeViajes/obtener'] for p in group]
    print('Vuelos',sum(str(t['Transporte']).lower() in ('avion','avión') for t in trips),'Micros',sum(str(t['Transporte']).lower()=='micro' for t in trips))
    for t in trips:
        if t['Nombre'].startswith('DEMO -'):
            check('POST','/autos/obtenerVS',{'vs_id':t['Codigo']})
    for p in packages:
        if p['Nombre'].startswith('DEMO -'):
            assert check('POST','/autos/obtenerPV',{'pv_id':p['Codigo']}),'Paquete demo sin auto'
            assert check('POST','/excursiones/obtenerPV',{'pv_id':p['Codigo']}),'Paquete demo sin excursión'
    check('POST','/autos/obtenerID',{'auto_id':2147483647},404)
    check('POST','/excursiones/obtenerID',{'excursion_id':2147483647},404)
    for path in ['/admin/pedidos','/admin/usuarios','/admin/ventas']:
        check('GET',path,expected=401)
    main.app.dependency_overrides[require_admin]=lambda:{'id':0}
    try:
        for path in ['/admin/resumen','/admin/usuarios','/admin/pedidos','/admin/ventas','/admin/auditoria','/admin/entregados','/admin/pendientes-entrega','/admin/cuenta-corriente?orden=fecha','/admin/cuenta-corriente?orden=cliente','/admin/solicitudes']:
            check('GET',path)
        for kind in ['viajes','paquetes','autos','excursiones']:
            check('GET',f'/admin/catalogo/{kind}')
            check('GET',f'/admin/catalogo/{kind}?eliminados=true')
    finally:main.app.dependency_overrides.pop(require_admin,None)
    print('Verificación de catálogo y consultas administrativas completada.')

if __name__=='__main__':verificar()
