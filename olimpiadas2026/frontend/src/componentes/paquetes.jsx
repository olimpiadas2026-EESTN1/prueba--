import { useEffect, useState, useContext } from "react";
import { AuthContext } from "../AuthContext";

const Paquetes = () => {
  const colores = [
    "#2d87f9", "#392df9", "#0b223e", "#1c549c", "#11335d",
    "#2265bb", "#162b86", "#082532", "#0e3e54"
  ];

  // Los paquetes también muestran precios en ARS para mantener coherencia con
  // la estrategia de venta y con el método de pago local que se utiliza en la app.
  const formatARS = (valor) =>
    new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(Number(valor || 0));

  const { listaCarrito, setListaCarrito } = useContext(AuthContext);
  const [loading, setLoading] = useState(true);
  const [mostrarDiv, setMostrarDiv] = useState(false);
  const [visibleDiv, setVisibleDiv] = useState(false);
  const [data, setData] = useState([]);
      const{dataPaquetes,setDataPaquetes}= useContext(AuthContext)
  const [vueloSeleccionado, setVueloSeleccionado] = useState(null);
const{ autos,setAutos}= useContext(AuthContext);
const {excursiones,setExcursiones} = useContext(AuthContext);
const {eleccionMoneda, setEleccionMoneda} =useContext(AuthContext);
const {precio,setPrecio} = useContext(AuthContext)
  const url = "https://backend-carrito-alpha.vercel.app/paqueteDeViajes/obtener";
 const url_autos = "https://backend-carrito-alpha.vercel.app/autos/obtener";
const url_exc =  "https://backend-carrito-alpha.vercel.app/excursiones/obtener";

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
      setListaCarrito(prev => {
        const existe = prev.some(item => item.Codigo === vueloSeleccionado.Codigo);
        return existe ? prev : [...prev, vueloSeleccionado];
      });
      handleCerrarDiv();
    }
  };
   useEffect(() => {
    const fetchData3 = async () => {
      try {
        const response = await fetch(url_exc);
        if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
        const json = await response.json();
        setExcursiones(json);
        setLoading(false);
      } catch (error) {
        console.error("Error al cargar los datos:", error);
        setLoading(false);
      }
    };

    fetchData3();
  }, []);
 useEffect(() => {
    const fetchDataa = async () => {
      try {
        const response = await fetch(url_autos);
        if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
        const json = await response.json();
        setAutos(json);
        setLoading(false);
      } catch (error) {
        console.error("Error al cargar los datos:", error);
        setLoading(false);
      }
    };

    fetchDataa();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
        const json = await response.json();
        setDataPaquetes(json)
        const vuelosConColor = json.flat().map((vuelo) => {
          const color = colores[Math.floor(Math.random() * colores.length)];
          return { ...vuelo, color };
        });

        setData(vuelosConColor);
        setLoading(false);
      } catch (error) {
        console.error("Error al cargar los datos:", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    localStorage.setItem("carrito", JSON.stringify(listaCarrito));
  }, [listaCarrito]);

  return (
    <div className="divConNombre fade-in-viajes">
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

      <h2 className="text_vuelos">Paquetes de vuelo</h2>

      <div className="container-div">
        {loading ? (
          <p className="parrafo_compra">Cargando vuelos disponibles...</p>
        ) : (
data.map((vuelo, index) => {
  const disponible = vuelo.Cupos > 0;

  return (
    <div
      key={index}
      role={disponible ? "button" : undefined}
      tabIndex={disponible ? "0" : undefined}
      onClick={() => {
        if (disponible) {
          setVueloSeleccionado(vuelo);
          handleAbrirDiv();
        }
      }}
      className={`vuelo ${!disponible ? "no-disponible" : ""}`}
      style={{
        backgroundColor: vuelo.color,
        cursor: disponible ? "pointer" : "not-allowed",
        opacity: disponible ? 1 : 0.5
      }}
    >
      <h1 className="titulo-compra">{vuelo.Destino}</h1>
      <p className="parrafo_compra">{formatARS(vuelo.Precio)}</p>
      
      <p className="parrafo_compra">{vuelo.Descripcion}</p>
      {!disponible && (
        <p className="parrafo_compra" style={{ fontWeight: "bold", color: "#c00" }}>
           No disponible
        </p>
      )}
    </div>
  );
})

        )}
      </div>
    </div>
  );
};

export default Paquetes;