import Autos from "./componentes/autos";
import Productos from "./componentes/productos";
import Ayuda from "./componentes/ayuda";
import MisPedidos from "./componentes/mis-pedidos";
import AdminPage from "./admin/AdminPage";
import { API_URL, apiFetch } from "./api";
import { Routes, Route, useLocation,useNavigate,Link } from 'react-router-dom' 
import './App.css'

import Login from './componentes/login'
import Layout from './componentes/layout'

import SingUp from './componentes/sing-up'
import Vuelos from './componentes/vuelos'
import Inside from './componentes/inside-image'
import Micros from './componentes/micros'
const url = `${API_URL}/viajes/obtener`;
import { AuthContext } from './AuthContext'
import { useContext,useEffect,useState } from 'react'
import Paquetes from './componentes/paquetes'
function App_header() {
  const [apiError, setApiError] = useState("");
  const navigate = useNavigate();
const {precio} =useContext(AuthContext)
 const {data, setData} =  useContext(AuthContext);
  const location = useLocation();
  const isHome = location.pathname === "/";
  const { isLoggedIn,setIsLoggedIn } = useContext(AuthContext);
  const {eleccionMoneda, setEleccionMoneda} =useContext(AuthContext);
  useEffect(() => {
  if (!isHome) return;
  setApiError("");
  apiFetch(url)
    .then(res => res.json())
    .then(json => {
      if (!Array.isArray(json)) throw new Error("El servidor no devolvió una lista de viajes.");
      setData(json);
    })
    .catch(error => setApiError(error.message));
}, [isHome, setData]);
  if (location.pathname === "/admin" || location.pathname.startsWith("/admin/")) return <AdminPage />;
  return (
    <>

  <main className="main-cont">
  {isHome && apiError && <p role="alert">{apiError}</p>}
  {location.pathname !== "/login" && location.pathname !== "/sing-up" && (
    <>

      <Inside showHero={isHome} />
      {isHome && <>

      {/* Rediseño principal: esta sección marca la nueva identidad premium de la agencia.
          Se trabajó en la narrativa del home para que parezca una landing más elegante,
          con un tono más turístico y premium que el diseño base. */}
      <div className="bienvenida">
        <span className="eyebrow">Tu próxima aventura empieza aquí</span>
        <h2>Viajá más alto, más lejos y con estilo.</h2>
        <p>Descubrí vuelos, escapadas y paquetes diseñados para hacer cada viaje más emocionante, cómodo y sin complicaciones.</p>
        <div className="bienvenida-actions">
          <button onClick={() => navigate("/vuelos")} className="btn-vuelos">
            Explorar vuelos
          </button>
          <button onClick={() => navigate("/paquetes")} className="btn-secondary">
            Ver paquetes
          </button>
        </div>
      </div>



      {/* El precio se estandarizó en ARS para evitar mezclas con USD.
          Esto refleja la realidad comercial del proyecto y simplifica la experiencia
          de compra para Mercado Pago y el público local. */}
      <div className="destinos-container">
        <h2 className="titulo-destino"> Destinos Populares</h2>
        <div className="tarjetas-destinos">
          {data?.length > 0 &&
            data.slice(0, 6).map((destino, i) => (
              <div key={i} className="tarjeta-destino">
                <h3>{destino.Destino}</h3>
                <p className="parrafo_compra">Desde {new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(destino.Precio)}</p>
              </div>
            ))}
        </div>
      </div>
            
      <div className="tips-viaje">
        <h2>💡 Tips para viajar más barato</h2>
        <ul>
          <li>🔍 Buscá con anticipación para encontrar mejores tarifas.</li>
          <li>📅 Sé flexible con tus fechas de viaje.</li>
          <li>🧳 Viajá liviano para evitar cargos por equipaje.</li>
        </ul>
      </div>
      </>}
    </>
  )}

  <Routes>
    <Route path="/" element={<Layout />}>
      <Route path="login" element={<Login />} />
      <Route path="sing-up" element={<SingUp />} />
      <Route path="vuelos" element={<Vuelos />} />
      <Route path="productos" element={<Productos />} />
      <Route path="ayuda" element={<Ayuda />} />
      <Route path="mis-pedidos" element={<MisPedidos />} />
      <Route path="autos" element={<Autos />} />
      <Route path="micros" element={<Micros />} />
      <Route path="paquetes" element={<Paquetes />} />
    </Route>
  </Routes>
</main>

      <footer className="footer">
  <div className="footer-content">
    <div>
      <h3>AirTrip Arg</h3>
      <p>Tu próxima aventura empieza con una buena idea ✈️</p>
    </div>
    <div>
      <h4>Enlaces</h4>
      <ul>
        <li><Link to={"/vuelos"}>Vuelos</Link></li>
        <li><Link to={"/paquetes"}>Paquetes</Link></li>
        <li><Link to={"/micros"}>Micros</Link></li>
        <li><Link to="/autos">Autos</Link></li>
        <li><Link to={"/login"}>Log in</Link></li>
        <li><Link to="/admin">Administración</Link></li>
      </ul>
    </div>
    <div>
      <h4>Contacto</h4>
      <p>📧 Lopezbacha07@gmail.com</p>
      <p>📍 Coronel Brandsen,Buenos Aires, Argentina</p>
    </div>
  </div>
  <p className="footer-copy">© {new Date().getFullYear()} AirTrip Arg. Todos los derechos reservados.</p>
</footer>

    </>
  );
}

export default App_header;