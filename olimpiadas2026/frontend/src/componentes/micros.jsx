import CategoryHeading from "./category-heading";
import { API_URL, apiFetch } from "../api";
import { useEffect, useState, useContext } from "react";
import { AuthContext } from "../AuthContext";

const Micros = () => {
  const colores = [
    "#2d87f9", "#392df9", "#0b223e", "#1c549c", "#11335d",
    "#2265bb", "#162b86", "#082532", "#0e3e54"
  ];

  // Este bloque mantiene la misma convención monetaria en viajes en micro:
  // el valor se presenta siempre en pesos argentinos para simplificar la compra.
  const formatARS = (valor) =>
    new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(Number(valor || 0));

  const { listaCarrito, setListaCarrito } = useContext(AuthContext);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [mostrarDiv, setMostrarDiv] = useState(false);
  const [visibleDiv, setVisibleDiv] = useState(false);
  const [data, setData] = useState(null);
  const [vueloSeleccionado, setVueloSeleccionado] = useState(null);
  const {eleccionMoneda, setEleccionMoneda} =useContext(AuthContext);
const {precio} =useContext(AuthContext)
  const url = `${API_URL}/viajes/obtener`;
  const handleAbrirDiv = () => {
    document.body.style.overflow = "hidden";
    setVisibleDiv(true);
    requestAnimationFrame(() => setMostrarDiv(true));
  };

  const handleCerrarDiv = () => {
    setMostrarDiv(false);
    document.body.style.overflow = "auto";
    setTimeout(() => setVisibleDiv(false), 300);
  };

  const handlerAgregar = () => {
    if (vueloSeleccionado) {

        setListaCarrito(prev => [...prev, vueloSeleccionado]);
      
      handleCerrarDiv();
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await apiFetch(url);
        if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
        const json = await response.json();

        const vuelosConColor = json.map((vuelo) => {
          const color = colores[Math.floor(Math.random() * colores.length)];
          return { ...vuelo, color };
        });

        setData(vuelosConColor);
        setLoading(false);
      } catch (error) {
        setErrorMessage(error.message);
        setLoading(false);
      }
    };
    fetchData();
  }, []);


  useEffect(() => {
    localStorage.setItem("carrito", JSON.stringify(listaCarrito));
  }, [listaCarrito]);

  const vuelosFiltrados = data?.filter((vuelo) => ['micro', 'bus', 'omnibus'].includes(String(vuelo.Transporte || "").trim().toLowerCase())) || [];

  return (
    
    <div className="divConNombre fade-in-viajes category-page">
      <CategoryHeading title="Viajes en micro" description="Encontrá tu próximo viaje por tierra y consultá horarios y cupos." />
      {errorMessage && <p role="alert">{errorMessage}</p>}
      
      {visibleDiv && vueloSeleccionado && (
        <>
          <div className="overlay fade-out" onClick={handleCerrarDiv}></div>
          <div className={`cont-compra ${mostrarDiv ? "fade-in" : "fade-out"}`}>
            <div className="descripcion">
              <div className="conjunto">
                <i className="fa-solid fa-chevron-up rari"></i>
                <h2 className="titulo-compra" style={{ color: vueloSeleccionado.color }}>
                  {vueloSeleccionado.Destino}
                </h2>
                   <p className="tipo_viaje">{vueloSeleccionado.Tipo_de_viaje}</p>
              </div>

              <h2 className="parrafo_compra">{formatARS(vueloSeleccionado.Precio)}</h2>
          
              <div className="conjunto">
                <i className="fa-solid fa-location-dot icon"></i>
                <p className="parrafo_compra">Origen: {vueloSeleccionado.Origen}</p>
              </div>

              <div className="conjunto">
               <i className="fa-solid fa-clock icon"></i>
                <p className="parrafo_compra">Duración: {vueloSeleccionado.Duracion}</p>
              </div>


              <div className="conjunto">
                <i className="fa-solid fa-calendar-days icon"></i>
                <p className="parrafo_compra">Fecha: {vueloSeleccionado.Fecha} - {vueloSeleccionado.Hora}</p>
              </div>

              <div className="conjunto">
                <i className="fa-solid fa-people-group icon"></i>
                <p className="parrafo_compra">Cupos disponibles: {vueloSeleccionado.Cupos}</p>
              </div>

              <div className="conjunto">
                <i className="fa-solid fa-plane-departure icon"></i>
                <p className="parrafo_compra">Transporte: {vueloSeleccionado.Transporte}</p>
              </div>

              <p className="parrafo_compra">{vueloSeleccionado.Descripcion}</p>

              <button
                onClick={handlerAgregar}
                className="boton-compra"
                style={{ color: vueloSeleccionado.color }}
              >
                <i style={{ color: vueloSeleccionado.color }} className="fa-solid fa-cart-shopping"></i> Añadir al carrito
              </button>
            </div>
          </div>
        </>
      )}

      <h2 className="text_vuelos">Opciones disponibles</h2>
      {loading && <p role="status">Cargando viajes…</p>}
      {!loading && !errorMessage && vuelosFiltrados.length === 0 && <p role="status">Todavía no hay viajes disponibles en esta categoría.</p>}
      <div className="container-div">
{vuelosFiltrados.map((vuelo, index) => {
  const disponible = vuelo.Cupos > 0;

  return (
    <div
      key={index}
      className={`vuelo ${!disponible ? "no-disponible" : ""}`}
      style={{
        backgroundColor: vuelo.color,
        cursor: disponible ? "pointer" : "not-allowed",
        opacity: disponible ? 1 : 0.5
      }}
      onClick={() => {
        if (disponible) {
          setVueloSeleccionado(vuelo);
          handleAbrirDiv();
        }
      }}
    >
      <h3 className="titulo-compra">{vuelo.Destino}</h3>
      <p className="parrafo_compra">{formatARS(vuelo.Precio)}</p>
      <p className="parrafo_compra">{vuelo.Descripcion}</p>
      {!disponible && (
        <p className="parrafo_compra" style={{ fontWeight: "bold", color: "#c00" }}>
           No disponible
        </p>
      )}
    </div>
  );
})}

      </div>
    </div>
  );
};

export default Micros;