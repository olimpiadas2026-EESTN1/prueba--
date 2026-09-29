export const API_URL = (
  import.meta.env.VITE_API_URL ||
  (
    import.meta.env.DEV
      ? "http://127.0.0.1:8000"
      : "https://backend-carrito-alpha.vercel.app"
  )
).replace(/\/$/, "");


export async function apiFetch(url, options = {}) {

  let response;

  try {

    response = await fetch(url, options);

  } catch (error) {

    console.error(
      "ERROR DE CONEXIÓN:",
      error
    );

    throw new Error(
      "No se pudo conectar con el servidor. Intentá nuevamente."
    );
  }


  // Intentamos leer la respuesta como JSON
  const data =
    await response
      .clone()
      .json()
      .catch(() => null);


  console.log("====================================");
  console.log("API FETCH");
  console.log("URL:", url);
  console.log("STATUS:", response.status);
  console.log("OK:", response.ok);
  console.log("RESPUESTA:", data);
  console.log("====================================");


  // =========================================================
  // ERROR 422
  // =========================================================

  if (response.status === 422) {

    console.error(
      "ERROR DE VALIDACIÓN 422:",
      data
    );

    throw new Error(
      data?.detail
        ? JSON.stringify(data.detail)
        : "Revisá los datos enviados al servidor."
    );
  }


  // =========================================================
  // ERROR HTTP
  // =========================================================

  if (!response.ok) {

    console.error(
      "ERROR HTTP:",
      data
    );

    throw new Error(

      data?.detail ||
      data?.error ||
      "No se pudo completar la solicitud."

    );
  }


  // =========================================================
  // ERROR DEVUELTO POR EL BACKEND
  // =========================================================

  if (
    data &&
    typeof data === "object" &&
    data.error
  ) {

    console.error(
      "ERROR DEVUELTO POR EL BACKEND:",
      data.error
    );

    console.error(
      "DETALLE:",
      data.detalle
    );


    let detalle = "";


    if (data.detalle) {

      detalle =
        typeof data.detalle === "string"
          ? data.detalle
          : JSON.stringify(
              data.detalle
            );
    }


    throw new Error(

      data.error +
      (
        detalle
          ? `\n\nDetalle: ${detalle}`
          : ""
      )

    );
  }


  return response;
}