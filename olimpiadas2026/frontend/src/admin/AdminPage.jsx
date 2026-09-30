import Gestion from "./Gestion";
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { AdminProvider, useAdmin } from './useAdmin';

const common = ['nombre', 'descripcion', 'precio', 'origen', 'destino', 'fecha', 'hora', 'cupos', 'tipo_de_viaje'];
const extra = { viajes: ['transporte', 'duracion_aprox'], paqueteDeViajes: ['estadia', 'tipo', 'duracion'] };

function Panel() {
  const { admin, login, logout, request } = useAdmin();
  const [section, setSection] = useState('viajes');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [revision, setRevision] = useState(0);
  async function submitLogin(event) {
    event.preventDefault(); const form = new FormData(event.currentTarget);
    setBusy(true); setMessage('');
    try { await login(form.get('email'), form.get('password')); }
    catch { setMessage('No se pudo ingresar. Revisá la cuenta administrativa y la conexión.'); }
    finally { setBusy(false); }
  }
  async function create(event) {
    event.preventDefault(); const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form));
    data.precio = Number(data.precio); data.cupos = Number(data.cupos);
    const [year, month, day] = data.fecha.split('-');
    data.fecha = `${day}/${month}/${year.slice(-2)}`;
    setBusy(true); setMessage('');
    try {
      await request(`/${section}/ingresar`, { method: 'POST', body: JSON.stringify(data) });
      form.reset(); setRevision(value => value + 1);
    } catch (error) { setMessage(error.message); }
    finally { setBusy(false); }
  }
  return <main className="admin-page">
    <Link to="/">← Volver a la tienda</Link>
    <h1>Administración / Vendedor</h1>
    {message && <p role="alert">{message}</p>}
    {!admin ? <form onSubmit={submitLogin} className="admin-form">
      <h2>Acceso administrativo</h2>
      <label>Correo<input name="email" type="email" autoComplete="username" required /></label>
      <label>Contraseña<input name="password" type="password" autoComplete="current-password" required /></label>
      <button disabled={busy}>{busy ? 'Ingresando…' : 'Ingresar'}</button>
      <p>Este acceso es independiente de la cuenta de comprador.</p>
    </form> : <>
      <p>Sesión de {admin.nombre}</p>
      <button onClick={() => logout().catch(() => setMessage('Sesión cerrada localmente. No se pudo contactar al servidor.'))}>Cerrar sesión administrativa</button>
      <Gestion revision={revision} />
      <h2>Alta de catálogo</h2>
      <nav className="admin-tabs" aria-label="Crear productos">
        {[['viajes','Nuevo vuelo o micro'],['paqueteDeViajes','Nuevo paquete']].map(([key,label])=><button key={key} aria-pressed={section===key} onClick={()=>setSection(key)}>{label}</button>)}
      </nav>
      {extra[section] && <form key={section} onSubmit={create} className="admin-form">
        <h2>Crear {section === 'viajes' ? 'viaje' : 'paquete'}</h2>
        {[...common, ...extra[section]].map(field => <label key={field}>{field.replaceAll('_', ' ')}
          {field === 'transporte' ? <select name={field}><option>Avion</option><option>Micro</option></select> : <input name={field} required type={['precio','cupos'].includes(field) ? 'number' : field === 'fecha' ? 'date' : field === 'hora' ? 'time' : 'text'} min={['precio','cupos'].includes(field) ? 1 : undefined} step={field === 'precio' ? '0.01' : undefined} />}
        </label>)}
        <button disabled={busy}>{busy ? 'Guardando…' : 'Guardar'}</button>
      </form>}
    </>}
  </main>;
}
export default function AdminPage() { return <AdminProvider><Panel /></AdminProvider>; }
