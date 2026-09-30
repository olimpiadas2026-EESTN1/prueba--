import { API_URL, apiFetch } from "../api";
import Login_buttons from "./buttons_login";
import Header_buttons from "./headers-buttons";
import { useNavigate } from "react-router-dom";

import { AuthContext } from "../AuthContext";
import { useContext, useState, useEffect } from "react";

const Inside = ({ showHero = true }) => {

  const { mail_guardado, setMail_guardado } =
    useContext(AuthContext);

  const [precioTotal, setPrecioTotal] = useState(0);

  const { listaCarrito, setListaCarrito } =
    useContext(AuthContext);

  const [mostarPaginaCompra, setMostarPaginaCompra] =
    useState(false);

  const navigate = useNavigate();

  const [mostrarCarrito, setMostrarCarrito] =
    useState(false);

  const [tieneCuotas, setTieneCoutas] =
    useState(false);

  const { isLoggedIn, setIsLoggedIn } =
    useContext(AuthContext);

  const { datos, setDatos } =
    useContext(AuthContext);

  const { dataPaquetes, setDataPaquetes } =
    useContext(AuthContext);

  const [filtroDestinoSect, setFiltroDestinoSect] =
    useState("");

  const [filtroPrecioSect, setFiltroPrecioSect] =
    useState("");

  const [animandoCierre, setAnimandoCierre] =
    useState(false);

  const [metodoPago, setMetodoPago] =
    useState(null);

  const { autos, setAutos } =
    useContext(AuthContext);

  const { excursiones, setExcursiones } =
    useContext(AuthContext);

  const [cuotas, setCuotas] =
    useState(3);

  const { eleccionMoneda, setEleccionMoneda } =
    useContext(AuthContext);

  // IMPORTANTE:
  // useContext devuelve un OBJETO, por eso usamos { }
  const { precio, setPrecio } =
    useContext(AuthContext);

  const urlDolar =
    "https://dolarapi.com/v1/dolares/oficial";

  const [paquetesFiltrados, setPaquetesFiltrados] =
    useState([]);

  const url =
    `${API_URL}/paqueteDeViajes/obtener`;


  // =========================================================
  // DÓLAR
  // =========================================================

  useEffect(() => {

    fetch(urlDolar)
      .then(data => data.json())
      .then(data => {
        setPrecio(data.compra);
      })
      .catch(error => {
        console.error(
          "Error obteniendo el precio del dólar:",
          error
        );
      });

  }, []);


  // =========================================================
  // LOGOUT
  // =========================================================

  const handleLogout = () => {
    const token = sessionStorage.getItem('buyer_token');
    if (token) fetch(`${API_URL}/clientes/cerrarSesion`, {method:'POST',headers:{Authorization:`Bearer ${token}`}}).catch(() => {});
    sessionStorage.removeItem('buyer_token');

    setIsLoggedIn(false);

    localStorage.removeItem("isLoggedIn");

    localStorage.removeItem("mail_guardado");

    setMail_guardado(null);

    navigate("/login");
  };


  // =========================================================
  // ABRIR CARRITO
  // =========================================================

  const handleAbrirCarrito = () => {

    setAnimandoCierre(false);

    setMostrarCarrito(true);
  };


  // =========================================================
  // CERRAR CARRITO
  // =========================================================

  const handleCerrarCarrito = () => {

    setAnimandoCierre(true);

    setTimeout(() => {
      setMostrarCarrito(false);
    }, 300);
  };


  // =========================================================
  // CALCULAR TOTAL
  // =========================================================

  useEffect(() => {

    const total = listaCarrito.reduce(
      (acc, vuelo) =>
        acc + parseInt(vuelo.Precio),
      0
    );

    setPrecioTotal(total);

  }, [listaCarrito]);


  // =========================================================
  // ABRIR PÁGINA DE COMPRA
  // =========================================================

  const handleComprar = () => {

    document.body.style.overflow = "hidden";

    setMostarPaginaCompra(true);

    setMostrarCarrito(false);
  };


  // =========================================================
  // CERRAR PÁGINA DE COMPRA
  // =========================================================

  const handleCerrarComprar = () => {

    document.body.style.overflow = "auto";

    setMostarPaginaCompra(false);
  };


  // =========================================================
  // MERCADO PAGO
  // =========================================================

  const handleEnviarVenta = async (event) => {

    event.preventDefault();

    console.log("====================================");
    console.log("INICIANDO PAGO");
    console.log("====================================");


    // ---------------------------------------------------------
    // VERIFICAR CARRITO
    // ---------------------------------------------------------

    if (
      !listaCarrito ||
      listaCarrito.length === 0
    ) {

      alert(
        "Tu carrito está vacío."
      );

      return;
    }


    // ---------------------------------------------------------
    // VERIFICAR LOGIN
    // ---------------------------------------------------------

    if (!mail_guardado) {

      alert(
        "Necesitás iniciar sesión antes de continuar con el pago."
      );

      return;
    }


    // ---------------------------------------------------------
    // VERIFICAR MÉTODO DE PAGO
    // ---------------------------------------------------------

    if (!metodoPago) {

      alert(
        "Seleccioná un método de pago."
      );

      return;
    }


    try {

      // -------------------------------------------------------
      // PREPARAR PRODUCTOS
      // -------------------------------------------------------

      const carritoParaMercadoPago =
        listaCarrito.map(
          (element, index) => {

            const precioProducto =
              Number(element.Precio);


            console.log(
              `PRODUCTO ${index + 1}:`,
              element
            );


            console.log(
              "PRECIO:",
              precioProducto
            );


            // Verificar destino

            if (!element.Destino) {

              throw new Error(
                `El producto ${index + 1} no tiene destino.`
              );
            }


            // Verificar precio

            if (
              !Number.isFinite(precioProducto) ||
              precioProducto <= 0
            ) {

              throw new Error(
                `El producto "${element.Destino}" tiene un precio inválido.`
              );
            }


            return {

              id: String(
                element.Codigo ||
                element.id ||
                element.Destino
              ),

              title: String(
                element.Destino ||
                "Producto AirTrip"
              ),

              unit_price:
                precioProducto,

              tipo: element.tipoProducto || (element.Transporte ? "viaje" : "paquete"),
              quantity: 1,
            };
          }
        );


      console.log(
        "===================================="
      );

      console.log(
        "PRODUCTOS QUE SE ENVIARÁN:"
      );

      console.log(
        carritoParaMercadoPago
      );

      console.log(
        "===================================="
      );


      // -------------------------------------------------------
      // ENVIAR AL BACKEND
      // -------------------------------------------------------

      const response =
        await apiFetch(
          `${API_URL}/carrito`,
          {

            method: "POST",

            headers: {
              Authorization: `Bearer ${sessionStorage.getItem("buyer_token") || ""}`,
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({

              items:
                carritoParaMercadoPago,

              user:
                mail_guardado,

            }),
          }
        );


      // -------------------------------------------------------
      // LEER RESPUESTA
      // -------------------------------------------------------

      const data =
        await response.json();


      console.log(
        "===================================="
      );

      console.log(
        "STATUS:",
        response.status
      );

      console.log(
        "OK:",
        response.ok
      );

      console.log(
        "RESPUESTA BACKEND:",
        data
      );

      console.log(
        "===================================="
      );


      // -------------------------------------------------------
      // ERROR HTTP
      // -------------------------------------------------------

      if (!response.ok) {

        throw new Error(

          data.detail ||
          data.error ||
          "El backend devolvió un error."

        );
      }


      // -------------------------------------------------------
      // ERROR DEVUELTO POR EL BACKEND
      // -------------------------------------------------------

      if (data.error) {

        console.error(
          "ERROR DE MERCADO PAGO:"
        );

        console.error(
          data.error
        );

        console.error(
          "DETALLE:",
          data.detalle
        );


        let detalle = "";


        if (data.detalle) {

          if (
            typeof data.detalle ===
            "string"
          ) {

            detalle =
              data.detalle;

          } else {

            detalle =
              JSON.stringify(
                data.detalle
              );
          }
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


      // -------------------------------------------------------
      // OBTENER URL DE MERCADO PAGO
      // -------------------------------------------------------

      const checkoutUrl =
        data.init_point ||
        data.sandbox_init_point;


      console.log(
        "===================================="
      );

      console.log(
        "URL MERCADO PAGO:"
      );

      console.log(
        checkoutUrl
      );

      console.log(
        "===================================="
      );


      // -------------------------------------------------------
      // VERIFICAR URL
      // -------------------------------------------------------

      if (!checkoutUrl) {

        throw new Error(
          "El backend no recibió una URL de Mercado Pago."
        );
      }


      // -------------------------------------------------------
      // REDIRECCIONAR
      // -------------------------------------------------------

      console.log(
        "REDIRIGIENDO A MERCADO PAGO..."
      );


      window.location.href =
        checkoutUrl;


    } catch (error) {

      console.error(
        "===================================="
      );

      console.error(
        "ERROR COMPLETO DEL PAGO:"
      );

      console.error(
        error
      );

      console.error(
        "===================================="
      );


      alert(

        "No se pudo iniciar el pago con Mercado Pago.\n\n" +
        error.message

      );
    }
  };


  // =========================================================
  // FILTROS
  // =========================================================

  const handlerFiltar = () => {

    let filtrado = [];


    if (
      filtroPrecioSect ===
      "menos90mil"
    ) {

      filtrado =
        dataPaquetes?.filter(
          (filtro) =>
            filtro[0].Tipo_de_viaje ===
              filtroDestinoSect &&
            filtro[0].Precio < 90000
        ) || [];


    } else if (
      filtroPrecioSect ===
      "mas90mil"
    ) {

      filtrado =
        dataPaquetes?.filter(
          (filtro) =>
            filtro[0].Tipo_de_viaje ===
              filtroDestinoSect &&
            filtro[0].Precio >= 90000 &&
            filtro[0].Precio <= 180000
        ) || [];


    } else if (
      filtroPrecioSect ===
      "mas180mil"
    ) {

      filtrado =
        dataPaquetes?.filter(
          (filtro) =>
            filtro[0].Tipo_de_viaje ===
              filtroDestinoSect &&
            filtro[0].Precio > 180000
        ) || [];
    }


    setPaquetesFiltrados(
      filtrado
    );
  };


  // =========================================================
  // OBTENER PAQUETES
  // =========================================================

  useEffect(() => {

    if (!showHero) return;


    const fetchData = async () => {

      try {

        const response =
          await apiFetch(url);


        if (!response.ok) {

          throw new Error(
            `Error ${response.status}: ${response.statusText}`
          );
        }


        const json =
          await response.json();


        setDataPaquetes(
          json
        );


      } catch (error) {

        console.error(
          "Error al cargar los datos:",
          error
        );
      }
    };


    fetchData();

  }, [showHero]);


  return <>

    <div
      className={`inside-image${
        showHero
          ? ""
          : " category-shell"
      }`}
    >

      <header className='header'>

        <div className="cont-header">

          <div
            className="brand-wordmark"
            onClick={() =>
              navigate("/")
            }
            role="button"
            tabIndex={0}
            aria-label="Ir al inicio"
          >

            <span className="brand-wordmark-main">
              AirTrip
            </span>

            <span className="brand-wordmark-sub">
              Arg
            </span>

          </div>


          <Header_buttons />


          {/* BOTÓN DE CARRITO */}

          <div className="icn">

            <img
              className="img-pais"
              src="https://ik.imagekit.io/dbqevvjt4/mundo.png?updatedAt=1751251555960"
              alt="imagen redonda de Argentina"
            />


            <span className="currency-pill">
              ARS
            </span>


            <Login_buttons />


            {isLoggedIn && (

              <div className="user-actions">

                <button
                  type="button"
                  className="account-button"
                  onClick={handleLogout}
                >
                  Cerrar sesión
                </button>

              </div>

            )}


            <button
              type="button"
              onClick={
                handleAbrirCarrito
              }
              className="cart-button"
              aria-label={`Abrir carrito, ${listaCarrito.length} productos`}
            >

              <svg
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >

                <path d="M2 3h3l3 12h11l3-9H6"/>

                <circle
                  cx="9"
                  cy="20"
                  r="1"
                />

                <circle
                  cx="18"
                  cy="20"
                  r="1"
                />

              </svg>


              <span>
                Carrito
              </span>


              <span className="cart-count">
                {listaCarrito.length}
              </span>

            </button>

          </div>

        </div>

      </header>


      {showHero && <>

        <div className="travel-hero">

          <div className="travel-copy">

            <span className="eyebrow">
              AirTrip Arg
            </span>


            <h1>
              Tu próxima escapada empieza aquí.
            </h1>


            <p>
              Encontrá vuelos, paquetes y experiencias diseñadas para vivir cada destino con más libertad y comodidad.
            </p>


            <div className="hero-actions">

              <button
                type="button"
                className="primary-btn"
                onClick={() =>
                  navigate("/vuelos")
                }
              >
                Buscar vuelos
              </button>


              <button
                type="button"
                className="secondary-btn"
                onClick={() =>
                  navigate("/paquetes")
                }
              >
                Ver paquetes
              </button>

            </div>

          </div>


          <div className="search-panel">

            <div className="panel-tabs">

              <button
                type="button"
                className="tab active"
              >
                Vuelos
              </button>


              <button
                type="button"
                className="tab"
              >
                Paquetes
              </button>


              <button
                type="button"
                className="tab"
              >
                Micros
              </button>

            </div>


            <form className="flight-form">

              <div className="field field-select">

                <label>
                  Tipo de viaje
                </label>


                <select
                  defaultValue="Ida y vuelta"
                >

                  <option>
                    Ida y vuelta
                  </option>

                  <option>
                    Solo ida
                  </option>

                  <option>
                    Multidestino
                  </option>

                </select>

              </div>


              <div className="route-grid">

                <button
                  type="button"
                  className="route-btn"
                >

                  <span>
                    Origen
                  </span>

                  <strong>
                    Buenos Aires
                  </strong>

                </button>


                <button
                  type="button"
                  className="swap-btn"
                  aria-label="Intercambiar destinos"
                >
                  ⇄
                </button>


                <button
                  type="button"
                  className="route-btn"
                >

                  <span>
                    Destino
                  </span>

                  <strong>
                    Madrid
                  </strong>

                </button>

              </div>


              <div className="field-row">

                <div className="field">

                  <label>
                    Salida
                  </label>

                  <input
                    type="date"
                    defaultValue="2026-11-12"
                  />

                </div>


                <div className="field">

                  <label>
                    Regreso
                  </label>

                  <input
                    type="date"
                    defaultValue="2026-11-20"
                  />

                </div>


                <div className="field">

                  <label>
                    Pasajeros
                  </label>


                  <select
                    defaultValue="2 personas"
                  >

                    <option>
                      1 persona
                    </option>

                    <option>
                      2 personas
                    </option>

                    <option>
                      3 personas
                    </option>

                    <option>
                      4 personas
                    </option>

                  </select>

                </div>

              </div>


              <button
                type="button"
                className="search-submit"
                onClick={() =>
                  navigate("/vuelos")
                }
              >
                Buscar vuelos
              </button>

            </form>

          </div>

        </div>


        <div className="quick-links">

          <div className="quick-link-card">

            <span>
              ✈️
            </span>

            <strong>
              Check-in
            </strong>

            <small>
              Gestioná tu vuelo
            </small>

          </div>


          <div className="quick-link-card">

            <span>
              🧳
            </span>

            <strong>
              Equipaje
            </strong>

            <small>
              Info y opciones
            </small>

          </div>


          <div className="quick-link-card">

            <span>
              🧾
            </span>

            <strong>
              Reservas
            </strong>

            <small>
              Revisa tus viajes
            </small>

          </div>

        </div>


        <div className="cont-filtros">

          <h1>
            Empezá a buscar tus vacaciones ideales
          </h1>


          <div className="seleccionar-filtro">

            <select
              onChange={(e) =>
                setFiltroDestinoSect(
                  e.target.value
                )
              }
            >

              <option value={undefined}>
                Elige un destino
              </option>

              <option value="Internacional">
                Internacional
              </option>

              <option value="Nacional">
                Nacional
              </option>

            </select>


            <select
              onChange={(e) =>
                setFiltroPrecioSect(
                  e.target.value
                )
              }
            >

              <option value={undefined}>
                Elige un rango de precio
              </option>

              <option value={"menos90mil"}>
                Menos de $90.000
              </option>

              <option value={"mas90mil"}>
                Mas de $90.000
              </option>

              <option value={"mas180mil"}>
                Mas de $180.000
              </option>

            </select>


            <button
              onClick={handlerFiltar}
              className="butoon"
            >
              Filtrar
            </button>

          </div>

        </div>

      </>}


      {/* =====================================================
          CARRITO
      ===================================================== */}

      {mostrarCarrito && (

        <div
          className={`carrito ${
            animandoCierre
              ? "fade-out"
              : "fade-in"
          }`}
        >

          <div className="encabezado_carrito">

            <a
              onClick={
                handleCerrarCarrito
              }
            >

              <h2 className="cerrar">
                X
              </h2>

            </a>


            <h1 className="titulo_carrito">
              Tu carrito
            </h1>

          </div>


          <div className="carrito-cont">

            {listaCarrito.map(
              (vuelo, index) => (

                <div
                  className="vuelo-carrito"
                  key={index}
                >

                  <h1 className="titulo-carrito">
                    {vuelo.Destino}
                  </h1>


                  {eleccionMoneda === "ARS" ? (

                    <p className="parrafo_carrito">
                      ${vuelo.Precio.toLocaleString()}ARS
                    </p>

                  ) : (

                    <p className="parrafo_carrito">
                      ${parseInt(
                        vuelo.Precio /
                        precio
                      )}USD
                    </p>

                  )}


                  <p className="parrafo_carrito">
                    {vuelo.Descripcion}
                  </p>


                  <hr />

                </div>

              )
            )}


            {listaCarrito.length > 0 && (

              <div>

                <p className="tet">
                  Total: ${precioTotal}
                </p>


                <button
                  className="boton-compra"
                  onClick={
                    handleComprar
                  }
                >
                  ir a comprar
                </button>


                <button
                  className="boton-compra"
                  onClick={() =>
                    setListaCarrito([])
                  }
                >
                  Vaciar carrito
                </button>

              </div>

            )}

          </div>

        </div>

      )}


      {/* =====================================================
          PÁGINA DE COMPRA
      ===================================================== */}

      {mostarPaginaCompra && (

        <>

          <div className="paginaCompra">

            <a
              onClick={
                handleCerrarComprar
              }
            >

              <h2 className="cerrarCompra">
                X
              </h2>

            </a>


            <h1 className="titulo-compra">
              ¡Termina tu compra!
            </h1>


            <div className="pagina-compra-cont">

              {listaCarrito.map(
                (vuelo, index) => (

                  <div
                    className="vuelo-carrito"
                    key={index}
                  >

                    <h2 className="titulo-carrito">
                      {vuelo.Destino}
                    </h2>


                    {eleccionMoneda === "ARS" ? (

                      <p className="parrafo_carrito">
                        ${vuelo.Precio.toLocaleString()}ARS
                      </p>

                    ) : (

                      <p className="parrafo_carrito">
                        ${parseInt(
                          vuelo.Precio /
                          precio
                        ).toLocaleString()}USD
                      </p>

                    )}


                    <p className="parrafo_carrito">
                      {vuelo.Descripcion}
                    </p>

                  </div>

                )
              )}

            </div>


            <label className="cont-compra-label">

              ¿Deseás realizar el pago en cuotas?


              <input
                type="checkbox"
                checked={tieneCuotas}
                onChange={(e) =>
                  setTieneCoutas(
                    e.target.checked
                  )
                }
              />

            </label>


            {tieneCuotas && (

              <>

                <label
                  className="cont-compra-label"
                  htmlFor="cuotas"
                >
                  Selecciona la cantidad de cuotas:
                </label>


                <select
                  id="cuotas"
                  value={cuotas}
                  onChange={(e) =>
                    setCuotas(
                      Number(
                        e.target.value
                      )
                    )
                  }
                >

                  <option value={3}>
                    3 cuotas
                  </option>

                  <option value={6}>
                    6 cuotas
                  </option>

                  <option value={9}>
                    9 cuotas
                  </option>

                  <option value={12}>
                    12 cuotas
                  </option>

                </select>

              </>

            )}


            <label
              className="cont-compra-label"
              htmlFor="m_pago"
            >
              Método de pago
            </label>


            <select
              id="m_pagos"
              onChange={(e) =>
                setMetodoPago(
                  e.target.value
                )
              }
            >

              <option value={undefined}>
                Selecciona un método de pago
              </option>

              <option value="Transferencia_bancaria">
                Transferencia bancaria
              </option>

              <option value="tarjeta_debito">
                Tarjeta de débito
              </option>

              <option value="tarjeta_credito">
                Tarjeta de crédito
              </option>

            </select>


            <h2>
              Total pagado: ${precioTotal}
            </h2>


            <button
              className="btn-vuelos"
              onClick={
                handleEnviarVenta
              }
            >
              Comprar
            </button>

          </div>

        </>

      )}

    </div>

  </>
}

export default Inside;