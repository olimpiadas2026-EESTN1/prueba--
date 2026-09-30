# Módulo de administración / vendedor

La versión ampliada y el alcance actual se describen en [Gestión relacional](gestion-relacional.md). Este documento explica la autenticación y el alta inicial.

## Alcance de la primera versión

Acceso independiente en `/admin`, listado y alta de viajes (vuelos/micros) y paquetes, y consulta de ventas. La versión ampliada agrega edición, usuarios, pedidos y auditoría; no incluye eliminación desde el panel, gestión de otros administradores ni confirmación automática de pagos.

El comprador sigue usando `AuthContext` y sus formularios. Administración usa `AdminProvider` y el hook `useAdmin`, ubicados en `src/admin/useAdmin.jsx`. No lee `isLoggedIn` del comprador ni guarda su token en localStorage. Al recargar o salir de la sección administrativa se debe ingresar otra vez. Cerrar esta sesión no cierra la del comprador.

## Backend

- `modulos/administradores.py`: consulta parametrizada de `usuario_administrativo`, verificación bcrypt, tokens aleatorios y sesiones con vencimiento de una hora.
- `roots/administradores.py`: `POST /admin/login`, `GET /admin/me` y `POST /admin/logout`.
- `require_admin`: valida `Authorization: Bearer <token>` en el servidor.
- Se retiró `/clientes/validarContrasenaAdmin` y la validación administrativa del módulo de compradores.
- Altas, eliminaciones y vínculos del catálogo, consultas privadas de clientes y todas las rutas de ventas requieren ahora sesión administrativa. El catálogo público y el login/registro de compradores siguen accesibles.
- `/carrito` conserva su comportamiento previo. No usar sus datos o el retorno del checkout como prueba de pago confirmado.

**Compatibilidad:** cualquier otro cliente que utilizara rutas privadas de ventas o de mantenimiento sin autenticación debe enviar ahora el token administrativo. El panel de comprador actual crea preferencias mediante `/carrito`.

## Crear el primer administrador

Se requiere la tabla `usuario_administrativo` con columnas `ua_id`, `nombre`, `apellido`, `contraseña` y `correo_electronico`. El script no crea ni modifica el esquema automáticamente.

Desde `backend`:

```sh
.venv/bin/python crear_admin.py
```

Pide nombre, apellido, correo y contraseña (sin mostrarla); valida confirmación, mínimo 12 caracteres y máximo 72 bytes. Al ejecutarlo, inserta una cuenta administrativa en la base configurada en `.env`. Guarda un hash bcrypt y rechaza un correo existente. No existe registro público de administradores. Las cuentas antiguas con contraseña en texto plano no son aceptadas por este login.

Seleccionar **Entrar como administrador** en el encabezado de la tienda o debajo del formulario de inicio de sesión. El enlace del encabezado también aparece con sesión de comprador iniciada. Ambos accesos abren `/admin`; ingresar allí con la cuenta administrativa. También se puede abrir `http://localhost:5173/admin` directamente. No compartir credenciales mediante Git.

## Uso

Seleccionar Vuelos y micros, Paquetes o Ventas. En las primeras dos secciones se puede completar el formulario y guardar. La fecha HTML se convierte a `dd/mm/yy`, formato esperado por el backend. El transporte se selecciona como Avion o Micro. En paquetes, usar Nacional/Internacional para `tipo_de_viaje` y solo ida/ida y vuelta para `tipo`.

## Pruebas ejecutadas

- `npm run build`: correcto.
- `.venv/bin/python -m unittest discover -s tests -v`: tres pruebas aprobadas, con múltiples verificaciones de rechazo sin token, token inventado, contraseña incorrecta, acceso válido, logout y vencimiento. Se simula la base; no se crean cuentas ni ventas reales.
- No se probó visualmente el panel ni un alta real en Supabase en esta entrega.

Para ejecutar las pruebas en otro equipo, instalar `requirements-dev.txt`.

## Límites para despliegue

Las sesiones se almacenan en memoria de un único proceso: reiniciar Uvicorn las invalida. Esta versión está orientada a desarrollo local con un worker. Antes de desplegar en Vercel/serverless o varios workers, usar un almacén compartido de sesiones y agregar limitación de intentos de login, HTTPS y auditoría administrativa. No se afirma que esta primera versión esté lista para producción.

Las operaciones CRUD existentes conservan sus validaciones y errores heredados, incluidos algunos errores devueltos con HTTP 200; el hook detecta `error` y no lo trata como éxito. Queda pendiente reforzar validaciones de negocio, edición y baja, permisos granulares, paginación y autenticación real del comprador.
