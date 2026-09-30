# AirTrip — Olimpiadas 2026

## Actualización: módulo de administrador / vendedor

La aplicación ahora cuenta con dos accesos separados: comprador y administrador. Seleccionar **Entrar como administrador** en el encabezado o en el formulario de login para abrir `/admin`.

El panel administrativo incluye:

- Resumen de usuarios, pedidos y ventas registradas.
- Búsqueda y edición de usuarios, con ficha e historiales relacionados.
- Historial de pedidos y ventas vinculados a cada comprador.
- Consulta y edición de viajes, paquetes, autos y excursiones; alta de viajes y paquetes.
- Auditoría de cambios y operaciones protegidas por sesión administrativa.

### Preparación para el equipo

1. Actualizar el repositorio y seguir la [guía de desarrollo local](olimpiadas2026/frontend/docs/desarrollo-local.md).
2. En otra base, aplicar `olimpiadas2026/backend/migrations/001_gestion.sql`. En el Supabase compartido ya fue aplicada; no elimina datos existentes.
3. Para crear una cuenta administrativa, ejecutar desde `backend`: `./.venv/bin/python crear_admin.py`. El script solicita los datos en la terminal y guarda la contraseña con bcrypt. No subir credenciales al repositorio.
4. Reiniciar el backend y volver a iniciar sesión en el frontend después de actualizar.

### Alcance y documentación

- [Acceso administrativo y creación de cuentas](olimpiadas2026/frontend/docs/administracion.md).
- [Gestión relacional, endpoints, permisos y pruebas](olimpiadas2026/frontend/docs/gestion-relacional.md).
- [Pantallas por categoría](olimpiadas2026/frontend/docs/pantallas-categorias.md).

Los pedidos se registran al iniciar el checkout; la conciliación de pagos para convertirlos automáticamente en ventas confirmadas sigue pendiente. Las sesiones actuales duran una hora y viven en un único proceso: antes de desplegar con varios workers o serverless se requiere un almacén compartido.

Validación: compilación del frontend y siete pruebas automatizadas del backend. Para ejecutar estas últimas, instalar `backend/requirements-dev.txt` y ejecutar desde `backend` `.venv/bin/python -m unittest discover -s tests -v`.
