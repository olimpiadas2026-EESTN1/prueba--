export const API_URL = (
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? "http://127.0.0.1:8000" : "https://backend-carrito-alpha.vercel.app")
).replace(/\/$/, "");

export async function apiFetch(url, options) {
  let response;
  try {
    response = await fetch(url, options);
  } catch {
    throw new Error("No se pudo conectar con el servidor. Intentá nuevamente.");
  }
  const data = await response.clone().json().catch(() => null);
  if (!response.ok || (data && typeof data === "object" && data.error)) {
    throw new Error(response.status === 422
      ? "Revisá los datos ingresados."
      : "No se pudo completar la solicitud. Intentá nuevamente.");
  }
  return response;
}
