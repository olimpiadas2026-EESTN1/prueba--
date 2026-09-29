# Preparar el proyecto después de actualizar

Desde la raíz del repositorio, ejecutar `git pull --ff-only` con el trabajo local guardado.

## Backend (macOS/Linux)

```sh
cd olimpiadas2026/backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn main:app --reload
```

En Windows, crear el entorno con `py -m venv .venv` y usar `.venv\Scripts\python.exe` en lugar de `.venv/bin/python`.

Crear `.env` en la raíz del repositorio (`prueba--/.env`), con `DATABASE_PASSWORD` y, para probar pagos, `MERCADOPAGO_TOKEN`. Obtener las credenciales por un canal privado; no subirlas a Git. La conexión usa el pooler de Supabase configurado en `backend/main.py`.

Revisar `http://127.0.0.1:8000/docs` y `/health`. El estado de configuración no verifica por sí solo la base: consultar también `/viajes/obtener`. La raíz `/` no tiene un endpoint definido. Si aparece `Address already in use`, ya hay un proceso en el puerto: usar el servidor existente o detenerlo desde su terminal antes de reiniciar.

## Frontend (otra terminal)

```sh
cd olimpiadas2026/frontend
npm install
npm run dev
```

Abrir la URL indicada por Vite. En desarrollo las consultas apuntan a `http://127.0.0.1:8000`; puede cambiarse con `VITE_API_URL` en `frontend/.env.local`. Reiniciar Vite después de modificar variables. No poner contraseñas ni tokens privados en variables `VITE_*`.

## Datos de demostración

Los datos de Supabase no se guardan en Git. Si todos usan el mismo proyecto, comparten los registros existentes. `backend/seed_demo.py` agrega seis viajes y tres paquetes identificados como demostración; requiere tablas existentes y modifica la base configurada. Ejecutarlo solo cuando se necesite poblar ese entorno:

```sh
cd olimpiadas2026/backend
.venv/bin/python seed_demo.py
```

El script conserva los registros existentes y omite los nombres de demostración que ya estén cargados. No crea el esquema. Los precios e itinerarios de demostración son ficticios.

## Validación

`npm run build` verifica la compilación del frontend. Ver [pantallas-categorias.md](pantallas-categorias.md) para el alcance y las pruebas de navegación. La confirmación de pagos, ventas y descuento de cupos requiere validación integral independiente.
