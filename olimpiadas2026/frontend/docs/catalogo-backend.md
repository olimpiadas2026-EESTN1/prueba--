# Catálogo de demostración y comprobación del backend

La revisión del 01/10 se concentra en catálogo y consultas administrativas. La integración Gmail queda a cargo del compañero que trabaja en paralelo; estos cambios no modifican su transporte ni autorización.

## Ejemplos disponibles

- Viajes: 7 (3 vuelos y 4 micros).
- Paquetes: 4.
- Autos: 6, incluyendo SUV en Bariloche, sedán en Mendoza, compacto en Iguazú y familiar en Mar del Plata.

Los nuevos productos llevan `DEMO` y precios ficticios. No constituyen reservas reales. Los paquetes DEMO de Bariloche, Mendoza e Iguazú tienen autos relacionados. Los viajes DEMO con destino en estas ciudades y Mar del Plata también tienen autos relacionados. Un viaje puede no tener auto asociado; en ese caso la API devuelve una lista vacía, no un error.

## Carga reproducible

Desde backend:

```sh
./.venv/bin/python seed_demo.py
```

El script agrega ejemplos faltantes por nombre, en una transacción, sin sobrescribir precios, cupos, fechas, datos reales ni restaurar registros eliminados. Repetirlo no duplica productos ni relaciones. Los vínculos nuevos se agregan solo a viajes y paquetes DEMO. Usa bloqueos durante la generación de identificadores para evitar colisiones entre ejecuciones simultáneas.

## Correcciones

- Consultar un auto inexistente devuelve 404.
- Las consultas de relaciones usan una consulta SQL con joins en vez de abrir otra conexión por cada resultado.
- Vínculos validan que ambos productos estén activos y no duplican asociaciones.
- Identificadores de relaciones no dependen de secuencias antiguas desincronizadas.
- Altas de catálogo con MAX+1 se serializan para evitar que dos administradores generen el mismo ID.
- Precios deben ser positivos y finitos, cupos y disponibilidad no negativos, identificadores positivos, fecha DD/MM/AA y hora HH:MM. Fechas u horas inválidas devuelven 422.

## Verificación

```sh
./.venv/bin/python -m unittest discover -s tests
./.venv/bin/python verificar_catalogo.py
```

La segunda comprobación lee la base real a través del cliente de pruebas de FastAPI: catálogos, relaciones, respuestas 404, protección 401 y consultas administrativas (pedidos, ventas, usuarios, auditoría, cuenta corriente, solicitudes e histórico). Sustituye la dependencia administrativa únicamente en el proceso de pruebas; no habilita acceso público al servidor. No modifica usuarios, no compra y no envía correos. No imprime credenciales ni datos personales.

Esta verificación no equivale a una compra real aprobada ni a una prueba de recepción de correos. Mercado Pago sigue requiriendo su prueba integral. Revisar las pantallas en la URL de entrega antes de capturar evidencias.
