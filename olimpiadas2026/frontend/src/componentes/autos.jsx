import { useContext, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { API_URL, apiFetch } from '../api';
import { AuthContext } from '../AuthContext';
import CategoryHeading from './category-heading';
import './autos.css';

const money = value => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(value);

export default function Autos() {
  const { listaCarrito, setListaCarrito } = useContext(AuthContext);
  const [autos, setAutos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cartMessage, setCartMessage] = useState('');
  const [revision, setRevision] = useState(0);
  const [search, setSearch] = useState('');
  const [availableOnly, setAvailableOnly] = useState(false);
  const [sort, setSort] = useState('modelo');

  useEffect(() => {
    let active = true;
    setLoading(true); setError('');
    apiFetch(`${API_URL}/autos/obtener`)
      .then(response => response.json())
      .then(data => {
        if (!Array.isArray(data)) throw new Error('El servidor no devolvió una lista de autos.');
        if (active) setAutos(data);
      })
      .catch(err => { if (active) setError(err.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [revision]);

  useEffect(() => {
    localStorage.setItem('carrito', JSON.stringify(listaCarrito));
  }, [listaCarrito]);

  const agregarAlquiler = auto => {
    const autoId = Number(auto['auto id']);
    if (listaCarrito.some(item => item.tipoProducto === 'auto' && Number(item.id) === autoId)) {
      setCartMessage(`${auto.modelo} ya está en el carrito.`);
      return;
    }

    setListaCarrito(previous => [...previous, {
      id: autoId,
      Codigo: autoId,
      Destino: auto.modelo,
      Precio: Number(auto['precio por dia']),
      Descripcion: 'Alquiler por día',
      tipoProducto: 'auto',
    }]);
    setCartMessage(`${auto.modelo} se agregó al carrito.`);
  };

  const shown = autos.filter(auto =>
    auto.modelo.toLocaleLowerCase('es').includes(search.trim().toLocaleLowerCase('es')) &&
    (!availableOnly || Number(auto.disponibles) > 0)
  ).sort((a, b) => sort === 'precio'
    ? Number(a['precio por dia']) - Number(b['precio por dia'])
    : a.modelo.localeCompare(b.modelo, 'es'));

  return <section className="category-page autos-page">
    <CategoryHeading title="Autos" description="Explorá los vehículos del catálogo y compará sus tarifas por día." />
    <div className="autos-filters">
      <label>Buscar modelo o destino<input type="search" value={search} onChange={e => setSearch(e.target.value)} placeholder="Ej.: Mendoza o SUV" /></label>
      <label>Ordenar por<select value={sort} onChange={e => setSort(e.target.value)}><option value="modelo">Modelo</option><option value="precio">Menor precio por día</option></select></label>
      <label className="autos-check"><input type="checkbox" checked={availableOnly} onChange={e => setAvailableOnly(e.target.checked)} /> Solo disponibles</label>
    </div>
    {loading ? <p role="status">Cargando autos…</p> : error ? <div role="alert"><p>{error}</p><button onClick={() => setRevision(r => r + 1)}>Reintentar</button></div> : <>
      <p className="autos-count" role="status">{shown.length} {shown.length === 1 ? 'auto encontrado' : 'autos encontrados'}</p>
      {cartMessage && <p className="autos-cart-message" role="status">{cartMessage}</p>}
      {!shown.length && <p>{autos.length ? 'No hay autos que coincidan con los filtros.' : 'Todavía no hay autos publicados.'}</p>}
      <div className="autos-grid">{shown.map(auto => <article className="auto-card" key={auto['auto id']}>
        <div className="auto-card-top"><span>Auto #{auto['auto id']}</span><span className={Number(auto.disponibles) > 0 ? 'auto-available' : 'auto-unavailable'}>{Number(auto.disponibles) > 0 ? 'Disponible' : 'Sin disponibilidad'}</span></div>
        <h2>{auto.modelo}</h2>
        <p className="auto-price">{money(Number(auto['precio por dia']))}<span> / día</span></p>
        <p>{auto.disponibles} {Number(auto.disponibles) === 1 ? 'unidad disponible' : 'unidades disponibles'}</p>
        {auto.modelo.startsWith('DEMO') && <p className="auto-demo">Vehículo y tarifa de demostración.</p>}
        <button type="button" className="auto-add" disabled={Number(auto.disponibles) < 1} onClick={() => agregarAlquiler(auto)}>
          Agregar alquiler al carrito
        </button>
      </article>)}</div>
    </>}
    <aside className="autos-info"><h2>Autos para acompañar tu viaje</h2><p>Las tarifas se calculan por día. Elegí las fechas de retiro y devolución al confirmar el pedido.</p><Link to="/paquetes">Explorar paquetes</Link><Link to="/vuelos">Ver vuelos</Link></aside>
  </section>;
}
