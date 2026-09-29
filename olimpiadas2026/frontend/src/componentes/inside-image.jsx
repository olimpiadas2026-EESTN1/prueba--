import Login_buttons from "./buttons_login"
import Header_buttons from "./headers-buttons"
import { data, useNavigate } from "react-router-dom";

  import { AuthContext } from "../AuthContext";
  import { useContext,useState,useEffect } from 'react'
  const Inside = ()=>{
  const { mail_guardado,setMail_guardado} = useContext(AuthContext);
  const [precioTotal,setPrecioTotal] = useState(0)
  const { listaCarrito, setListaCarrito} = useContext(AuthContext);
  const [mostarPaginaCompra,setMostarPaginaCompra] = useState(false)
  const navigate = useNavigate();
  const [mostrarCarrito, setMostrarCarrito] = useState(false);
  const [tieneCuotas, setTieneCoutas] = useState(false)
  const { isLoggedIn,setIsLoggedIn } = useContext(AuthContext);
  const {datos,setDatos} =  useContext(AuthContext);
  const{dataPaquetes,setDataPaquetes}= useContext(AuthContext)
  const [filtroDestinoSect,setFiltroDestinoSect] = useState("")
  const [filtroPrecioSect,setFiltroPrecioSect] = useState("")
  const [animandoCierre, setAnimandoCierre] = useState(false); 
  const [metodoPago, setMetodoPago] = useState(null); 
  const{ autos,setAutos}= useContext(AuthContext);
  const {excursiones,setExcursiones} = useContext(AuthContext);
  const [cuotas, setCuotas] = useState(3);
  const {eleccionMoneda, setEleccionMoneda} =useContext(AuthContext);
  const {precio,setPrecio} =useContext(AuthContext)
  const urlDolar="https://dolarapi.com/v1/dolares/oficial"
  const [paquetesFiltrados,setPaquetesFiltrados] = useState([])
  const url = "https://backend-carrito-alpha.vercel.app/paqueteDeViajes/obtener";
    useEffect(() => {
  fetch(urlDolar)
  .then(data => data.json())
  .then(data=>setPrecio(data.compra))
  
    }, []);
  const handleLogout = () => {
    setIsLoggedIn(false);
    localStorage.removeItem("isLoggedIn"); 
    localStorage.removeItem("mail_guardado");
 setMail_guardado(null)
 
 
  
    navigate("/login"); 
  };
    const handleAbrirCarrito = () => {
  setAnimandoCierre(false)
   setMostrarCarrito(true)
  };
      const handleCerrarCarrito = () => {
        setAnimandoCierre(true)
   setTimeout(() => setMostrarCarrito(false), 300);
  };
     useEffect(() => {
  const total = listaCarrito.reduce((acc, vuelo) => acc + parseInt(vuelo.Precio), 0);
  setPrecioTotal(total);
}, [listaCarrito]);

const handleComprar = () =>{
   document.body.style.overflow = "hidden";
  setMostarPaginaCompra(true)
    setMostrarCarrito(false)
  
}
const handleCerrarComprar = ()=>{
   document.body.style.overflow = "auto";
  setMostarPaginaCompra(false)
}
const handleEnviarVenta = async (event) => {
  event.preventDefault();

  if (!listaCarrito.length) {
    alert("Tu carrito está vacío.");
    return;
  }

  if (!mail_guardado) {
    alert("Necesitás iniciar sesión antes de continuar con el pago.");
    return;
  }

  try {
    const carritoParaMercadoPago = listaCarrito.map((element) => ({
      id: element.Codigo || element.id || element.Destino,
      title: element.Destino,
      unit_price: Number(element.Precio),
      quantity: 1,
    }));

    const response = await fetch("https://backend-carrito-alpha.vercel.app/carrito", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        items: carritoParaMercadoPago,
        user: mail_guardado,
      }),
    });

    const data = await response.json();

    if (!response.ok || !data.sandbox_init_point) {
      throw new Error(data.error || "No se pudo crear la preferencia de pago.");
    }

    window.location.href = data.sandbox_init_point;
  } catch (error) {
    console.error("Error al crear la preferencia de Mercado Pago:", error);
    alert("No se pudo iniciar el pago con Mercado Pago. Intentalo nuevamente.");
  }
};
const handlerFiltar = () => {
  let filtrado = [];

  if (filtroPrecioSect === "menos90mil") {
    filtrado = dataPaquetes?.filter(
      (filtro) => filtro[0].Tipo_de_viaje === filtroDestinoSect && filtro[0].Precio < 90000
    ) || [];
  } else if (filtroPrecioSect === "mas90mil") {
    filtrado = dataPaquetes?.filter(
      (filtro) =>
        filtro[0].Tipo_de_viaje === filtroDestinoSect &&
        filtro[0].Precio >= 90000 &&
        filtro[0].Precio <= 180000
    ) || [];
  } else if (filtroPrecioSect === "mas180mil") {
    filtrado = dataPaquetes?.filter(
      (filtro) => filtro[0].Tipo_de_viaje === filtroDestinoSect && filtro[0].Precio > 180000
    ) || [];
  }

  
  setPaquetesFiltrados(filtrado);
};

useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
        const json = await response.json();
        setDataPaquetes(json)

      } catch (error) {
        console.error("Error al cargar los datos:", error);
       
      }
    };

    fetchData();
  }, []);
 
return <>
     
  {/* Bloque visual principal del landing.
      Se mantuvo una estética tipo agencia de viajes con fondo de imagen,
      cabecera glassmorphism y botones más armónicos con el resto del diseño. */}
<div className='inside-image'>
  <header className='header'>
    <div className="cont-header">
        
        <div className="brand-wordmark" onClick={() => navigate("/")} role="button" tabIndex={0} aria-label="Ir al inicio">
          <span className="brand-wordmark-main">AirTrip</span>
          <span className="brand-wordmark-sub">Arg</span>
        </div>
        <Header_buttons />
        {/* BOTÓN DE CARRITO */}
        <div className="icn">
          <img className="img-pais" src="https://ik.imagekit.io/dbqevvjt4/mundo.png?updatedAt=1751251555960" alt="imagen redonda de Argentina" />
          {/* La moneda se dejó fija en ARS para reforzar el uso local del negocio.
              Se eliminó la lógica de switching USD/ARS para mantener una sola referencia
              de precio y evitar confusión en pagos, compras y promociones. */}
          <span className="currency-pill">ARS</span>
           {/* BOTONES PARA LOGEARSE */}
        <Login_buttons />
        {/* BOTÓN PARA DESLOGEARSE */}
        {isLoggedIn && (
          <div className="user-actions">
            <a className="link" onClick={handleLogout} href="#">Log out</a>
          </div>
        )}
        <a onClick={handleAbrirCarrito} className="link"><i className="fa-solid fa-cart-shopping" ></i></a>
        </div>
    </div>

  </header>

 {/* HERO DE BUSQUEDA */}
 <div className="travel-hero">
  <div className="travel-copy">
    <span className="eyebrow">AirTrip Arg</span>
    <h1>Tu próxima escapada empieza aquí.</h1>
    <p>Encontrá vuelos, paquetes y experiencias diseñadas para vivir cada destino con más libertad y comodidad.</p>
    <div className="hero-actions">
      <button type="button" className="primary-btn" onClick={() => navigate("/vuelos")}>Buscar vuelos</button>
      <button type="button" className="secondary-btn" onClick={() => navigate("/paquetes")}>Ver paquetes</button>
    </div>
  </div>

  <div className="search-panel">
    <div className="panel-tabs">
      <button type="button" className="tab active">Vuelos</button>
      <button type="button" className="tab">Paquetes</button>
      <button type="button" className="tab">Micros</button>
    </div>

    <form className="flight-form">
      <div className="field field-select">
        <label>Tipo de viaje</label>
        <select defaultValue="Ida y vuelta">
          <option>Ida y vuelta</option>
          <option>Solo ida</option>
          <option>Multidestino</option>
        </select>
      </div>

      <div className="route-grid">
        <button type="button" className="route-btn">
          <span>Origen</span>
          <strong>Buenos Aires</strong>
        </button>
        <button type="button" className="swap-btn" aria-label="Intercambiar destinos">⇄</button>
        <button type="button" className="route-btn">
          <span>Destino</span>
          <strong>Madrid</strong>
        </button>
      </div>

      <div className="field-row">
        <div className="field">
          <label>Salida</label>
          <input type="date" defaultValue="2026-11-12" />
        </div>
        <div className="field">
          <label>Regreso</label>
          <input type="date" defaultValue="2026-11-20" />
        </div>
        <div className="field">
          <label>Pasajeros</label>
          <select defaultValue="2 personas">
            <option>1 persona</option>
            <option>2 personas</option>
            <option>3 personas</option>
            <option>4 personas</option>
          </select>
        </div>
      </div>

      <button type="button" className="search-submit" onClick={() => navigate("/vuelos")}>Buscar vuelos</button>
    </form>
  </div>
 </div>

 <div className="quick-links">
  <div className="quick-link-card">
    <span>✈️</span>
    <strong>Check-in</strong>
    <small>Gestioná tu vuelo</small>
  </div>
  <div className="quick-link-card">
    <span>🧳</span>
    <strong>Equipaje</strong>
    <small>Info y opciones</small>
  </div>
  <div className="quick-link-card">
    <span>🧾</span>
    <strong>Reservas</strong>
    <small>Revisa tus viajes</small>
  </div>
 </div>

 {/* SELECCIÓN DE VUELOS POR FILTROS */}
 <div className="cont-filtros">
  <h1>Empezá a buscar tus vacaciones ideales</h1>

  {/* Seleccionar un destino para filtrar */}
  <div className="seleccionar-filtro">
<select  onChange={(e) => setFiltroDestinoSect(e.target.value)}>
  <option value={undefined}>Elige un destino</option>
<option value="Internacional">Internacional</option>
<option value="Nacional">Nacional</option>
</select>
 {/* Seleccionar un rango de precio para filtrar */}
<select onChange={(e) => setFiltroPrecioSect(e.target.value)}>
  <option value={undefined}>Elige un rango de precio</option>
  <option value={"menos90mil"}>Menos de $90.000</option>
  <option value={"mas90mil"}>Mas de $90.000</option>
  <option value={"mas180mil"}>Mas de $180.000</option>
</select>
<button onClick={handlerFiltar} className="butoon">Filtrar</button>
  </div>
 </div>
  {/* CARRITO */}
{mostrarCarrito && (
  <div className={`carrito ${animandoCierre ? "fade-out" : "fade-in"}`}>
        <div className="encabezado_carrito">
            <a onClick={handleCerrarCarrito} ><h2 className="cerrar">X</h2></a>
            <h1 className="titulo_carrito">Tu carrito</h1>       
        </div>
        <div className="carrito-cont">
           { listaCarrito.map((vuelo, index) => (           
            <div className="vuelo-carrito"key={index}>
              <h1 className="titulo-carrito">{vuelo.Destino}</h1>
              
            {eleccionMoneda ==="ARS" ?(
            <p className="parrafo_carrito">${vuelo.Precio.toLocaleString()}ARS</p>
          ):(
            <p className="parrafo_carrito">${parseInt(vuelo.Precio/precio)}USD</p>
          )
          }
            
              <p className="parrafo_carrito">{vuelo.Descripcion}</p>
              <hr />     
            </div>            
           ))}
         {listaCarrito.length > 0 && (
  <div>
    <p className="tet">Total: ${precioTotal}</p>
    <button className="boton-compra" onClick={handleComprar}>ir a comprar</button>
    <button className="boton-compra" onClick={() => setListaCarrito([])}>
      Vaciar carrito
    </button>
  </div>
)}
        </div>
  </div>
)}
{/* PAGINA DE COMPRA, CUANDO CLIQUEAS COMPRAR EN EL CARRITO */}
{mostarPaginaCompra &&(
          <>
<div className="paginaCompra">
  <a onClick={handleCerrarComprar} ><h2 className="cerrarCompra">X</h2></a>
  <h1 className="titulo-compra">¡Termina tu compra!</h1>
  <div className="pagina-compra-cont">
        {listaCarrito.map((vuelo, index) => (
      <div className="vuelo-carrito" key={index}>
        <h2 className="titulo-carrito">{vuelo.Destino}</h2>
                                                     {eleccionMoneda ==="ARS" ?(
            <p className="parrafo_carrito">${vuelo.Precio.toLocaleString()}ARS</p>
          ):(
            <p className="parrafo_carrito">${parseInt(vuelo.Precio/precio).toLocaleString()}USD</p>
          )
          }
       
        <p className="parrafo_carrito">{vuelo.Descripcion}</p>
      </div>
    ))}
  </div>
    <label className="cont-compra-label">
      ¿Deseás realizar el pago en cuotas?
      <input
        type="checkbox"
        checked={tieneCuotas}
        onChange={(e) => setTieneCoutas(e.target.checked)}
      />
    </label>
    {tieneCuotas && (
  <>
    <label className="cont-compra-label" htmlFor="cuotas">Selecciona la cantidad de cuotas:</label>
    <select id="cuotas" value={cuotas} onChange={(e) => setCuotas(Number(e.target.value))}>
      <option value={3}>3 cuotas</option>
      <option value={6}>6 cuotas</option>
      <option value={9}>9 cuotas</option>
      <option value={12}>12 cuotas</option>
    </select>
  </>
)}<label className="cont-compra-label" htmlFor="m_pago">Método de pago</label>
    <select id="m_pagos"  onChange={(e) => setMetodoPago(e.target.value)}>
       <option value={undefined}>Selecciona un método de pago</option>
      <option value="Transferencia_bancaria">Transferencia bancaria</option>
      <option value="tarjeta_debito">Tarjeta de débito</option>
      <option value="tarjeta_credito">Tarjeta de crédito</option>
    
    </select>

  <h2>Total pagado: ${precioTotal}</h2>
    <button className="btn-vuelos" onClick={handleEnviarVenta}>Comprar</button>
</div>

          </>
        )}
</div>

    </>
}
export default Inside