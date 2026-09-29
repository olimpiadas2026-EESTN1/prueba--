# Pantallas por categoría

## Objetivo y alcance

Separar Inicio, Vuelos, Micros y Paquetes para que cada sección tenga un propósito claro. Esto es navegación por categorías, no paginación de resultados. No se agregaron números de página ni se modificó la API.

La dificultad es baja a moderada: las rutas ya existían; el trabajo consiste en separar la portada del catálogo sin perder sesión, navegación ni carrito.

## Comportamiento

| Ruta | Contenido principal | Fuente de datos |
| --- | --- | --- |
| `/` | Portada, accesos y destinos populares | `/viajes/obtener` y `/paqueteDeViajes/obtener` |
| `/vuelos` | Título, descripción y catálogo de aviones | `/viajes/obtener`, filtrado por Avion/Avión |
| `/micros` | Título, descripción y catálogo terrestre | `/viajes/obtener`, filtrado por Micro/Bus/Omnibus |
| `/paquetes` | Título, descripción y paquetes | `/paqueteDeViajes/obtener` |

Las categorías conservan encabezado, carrito, sesión y pie de página. La portada, sus promociones y formularios no se repiten encima de los resultados. El enlace activo indica la ubicación actual. Cada categoría permite volver a Inicio.

## Implementación

- `src/App.jsx`: muestra las secciones promocionales solo en `/`; consulta destinos populares solo cuando Inicio está activo.
- `src/componentes/inside-image.jsx`: `showHero` controla la portada; el encabezado y los paneles del carrito siguen montados al navegar entre categorías. La consulta de paquetes de la portada se omite en categorías.
- `src/componentes/headers-buttons.jsx`: navegación semántica con `NavLink`, estado activo y `aria-current`.
- `src/componentes/category-heading.jsx`: título H1, descripción, enlace a Inicio, título del documento y foco al ingresar a una categoría.
- `vuelos.jsx`, `micros.jsx`, `paquetes.jsx`: incorporan el encabezado común y conservan selección, disponibilidad y carrito.
- `src/App.css`: encabezado compacto y distribución adaptable a pantallas pequeñas.

## Criterios considerados

1. **Separación de contenido:** mostrar el catálogo al entrar, sin obligar a recorrer toda la portada.
2. **Continuidad:** cambiar de ruta no debe borrar sesión ni carrito; ambos siguen en `AuthContext`.
3. **Accesibilidad:** navegación identificada, categoría activa, un título principal y foco en ese título al entrar; controles utilizables con teclado.
4. **Móvil:** títulos fluidos, encabezado adaptable y grilla de tarjetas responsive.
5. **Datos:** se conserva el contrato actual, incluidos los arrays anidados de paquetes. No se generan datos ficticios en el frontend cuando falla la API.
6. **Estados:** conservar carga, error y ausencia de resultados; no confundir un catálogo vacío con una desconexión.
7. **Rendimiento:** evitar consultas de la portada en categorías. Los endpoints aún devuelven el catálogo completo; si crece, evaluar filtrado y paginación desde el backend.
8. **URLs:** enlaces directos y navegación Atrás/Adelante usan React Router. En producción, el hosting debe redirigir rutas SPA como `/vuelos` a `index.html`; esto no se configura en este cambio.
9. **Compras:** no cambia precios, cupos ni confirmación de pagos. La verificación integral de compra sigue siendo un trabajo separado.

## Validación y límites

Validación ejecutada: `npm run build` correcto y 20 comprobaciones de renderizado aprobadas (5 por ruta: contenido específico, carrito presente, portada solo en Inicio, destinos populares solo en Inicio y navegación activa). Se utilizó renderizado de React en Node; no se ejecutaron efectos ni consultas de red en esta prueba. Esta comprobación no sustituye una prueba visual ni el flujo completo con un navegador.

Lista de aceptación manual:

- Abrir `/`: se ve la portada y sus accesos.
- Entrar en cada categoría: no aparece la portada, el título y enlace activo son correctos.
- Agregar un producto y cambiar de categoría: el contador y contenido del carrito se conservan.
- Repetir con sesión iniciada y cerrada; el carrito sigue visible.
- Probar Atrás/Adelante, enlace directo y recarga de cada URL.
- Revisar ancho móvil, teclado y apertura/cierre de detalles y carrito.
- Probar API detenida y catálogo vacío, sin confundir esos estados.

Limitaciones previas: los formularios decorativos de la portada no implementan todos los filtros que muestran; los diálogos existentes requieren una revisión específica de accesibilidad. Esta entrega organiza las pantallas y no afirma completar esos flujos.
