export const API_URL = import.meta.env.DEV
  ? 'http://127.0.0.1:8000'
  : 'https://prueba-pdhd.vercel.app';

export async function apiFetch(url, options = {}) {
  let response;

  try {
    response = await fetch(url, options);
  } catch {
    throw new Error(
      'No se pudo conectar con el servidor. Intentá nuevamente.'
    );
  }

  const data = await response.clone().json().catch(() => null);

  if (response.status === 401 && url.endsWith('/carrito')) {
    window.dispatchEvent(new Event('buyer-session-expired'));
  }

  if (!response.ok || data?.error) {
    throw new Error(
      typeof data?.detail === 'string'
        ? data.detail
        : response.status === 422
          ? 'Revisá los datos ingresados.'
          : 'No se pudo completar la solicitud. Intentá nuevamente.'
    );
  }

  return response;
}
