import { useEffect, useState } from 'react';
import { useAdmin } from './useAdmin';
const entities = [['resumen','Resumen'],['usuarios','Usuarios'],['pedidos','Pedidos'],['ventas','Ventas'],['viajes','Vuelos y micros'],['paquetes','Paquetes'],['autos','Autos'],['excursiones','Excursiones'],['auditoria','Cambios']];
const fields = {usuarios:['nombre','apellido','correo_electronico'], viajes:['nombre','descripcion','precio','cupos','estado'], paquetes:['nombre','descripcion','precio','cupos','estado'], autos:['modelo','disponibles','precio_por_dia'], excursiones:['nombre','descripcion','lugar']};
const keys = {usuarios:'id',viajes:'codigo',paquetes:'codigo',autos:'auto_id',excursiones:'excursion_id'};
function Cell({ value }) { return typeof value === 'object' && value !== null ? <details><summary>Ver detalle</summary><pre>{JSON.stringify(value,null,2)}</pre></details> : String(value ?? '—'); }
function Table({ rows, onUser, onEdit }) {
 if (!rows.length) return <p>No hay registros.</p>;
 const cols=Object.keys(rows[0]);
 return <div className="admin-table"><table><thead><tr>{cols.map(k=><th key={k}>{k.replaceAll('_',' ')}</th>)}{(onUser||onEdit)&&<th>Acciones</th>}</tr></thead><tbody>{rows.map((row,i)=><tr key={row.id ?? i}>{cols.map(k=><td key={k}><Cell value={row[k]}/></td>)}{(onUser||onEdit)&&<td>{onUser&&(row.uc_id||row.email)&&<button onClick={()=>onUser(row.uc_id ?? row.id)}>Ver cuenta e historial</button>}{onEdit&&<button onClick={()=>onEdit(row)}>Editar</button>}</td>}</tr>)}</tbody></table></div>;
}
export default function Gestion({ revision }) {
 const { request }=useAdmin();
 const [section,setSection]=useState('resumen');
 const [query,setQuery]=useState(''); const [search,setSearch]=useState('');
 const [data,setData]=useState(null); const [error,setError]=useState('');
 const [profile,setProfile]=useState(null); const [edit,setEdit]=useState(null);
 const [version,setVersion]=useState(0); const [busy,setBusy]=useState(false);
 useEffect(()=>{
  let active=true; setData(null); setError(''); setProfile(null); setEdit(null);
  const path=['resumen','usuarios','pedidos','ventas','auditoria'].includes(section)?`/admin/${section}`:`/admin/catalogo/${section}`;
  request(path+(section==='usuarios'?`?q=${encodeURIComponent(search)}`:'')).then(d=>{if(active)setData(d);}).catch(e=>{if(active)setError(e.message);});
  return ()=>{active=false;};
  // eslint-disable-next-line react-hooks/exhaustive-deps
 },[section,search,version,revision]);
 async function showUser(id) {setError('');try {setProfile(await request(`/admin/usuarios/${id}`));} catch(e){setError(e.message);}}
 async function save(event) {
  event.preventDefault();setBusy(true);setError('');
  const values=Object.fromEntries(new FormData(event.currentTarget));
  for(const k of ['precio','cupos','disponibles','precio_por_dia'])if(k in values)values[k]=Number(values[k]);
  try {await request(`/admin/datos/${section}/${edit[keys[section]]}`,{method:'PATCH',body:JSON.stringify(values)});setEdit(null);setVersion(v=>v+1);}catch(e){setError(e.message);}finally{setBusy(false);}
 }
 return <section aria-label="Gestión de la empresa">
  <nav className="admin-tabs" aria-label="Gestión">{entities.map(([key,label])=><button key={key} aria-pressed={section===key} onClick={()=>setSection(key)}>{label}</button>)}</nav>
  <h2>{entities.find(([k])=>k===section)[1]}</h2>
  <button onClick={()=>setVersion(v=>v+1)}>Actualizar datos</button>
  {section==='usuarios'&&<form onSubmit={e=>{e.preventDefault();setSearch(query);}} className="admin-search"><label>Buscar por nombre o correo <input value={query} onChange={e=>setQuery(e.target.value)}/></label><button>Buscar</button></form>}
  {error&&<p role="alert">{error}</p>}
  {!data&&!error&&<p role="status">Cargando datos de la base…</p>}
  {data&&(section==='resumen'?<div className="admin-stats">{Object.entries(data).map(([k,v])=><article key={k}><h3>{k.replaceAll('_',' ')}</h3><strong>{v}</strong></article>)}</div>:<><p>Hasta 200 registros recientes. Los pedidos pendientes no se contabilizan como ventas.</p><Table rows={data} onUser={['usuarios','pedidos','ventas'].includes(section)?showUser:null} onEdit={fields[section]?setEdit:null}/></>)}
  {profile&&<section className="admin-detail"><button onClick={()=>setProfile(null)}>Cerrar ficha</button><h2>Cuenta de {profile.usuario.nombre} {profile.usuario.apellido}</h2><p>Usuario #{profile.usuario.id} · {profile.usuario.email}</p><h3>Historial de pedidos</h3><Table rows={profile.pedidos}/><h3>Historial de ventas registradas</h3><Table rows={profile.ventas}/></section>}
  {edit&&<form className="admin-form" onSubmit={save}><h3>Editar registro #{edit[keys[section]]}</h3>{fields[section].map(f=><label key={f}>{f.replaceAll('_',' ')}{f==='estado'?<select name={f} defaultValue={edit[f]}><option>Disponible</option><option>No disponible</option></select>:<input required name={f} defaultValue={edit[f]??(f==='correo_electronico'?edit.email:'')} type={['precio','cupos','disponibles','precio_por_dia'].includes(f)?'number':f==='correo_electronico'?'email':'text'} min="0" step={f.includes('precio')?'0.01':'1'}/>}</label>)}<button disabled={busy}>{busy?'Guardando…':'Guardar cambios'}</button><button type="button" onClick={()=>setEdit(null)}>Cancelar</button></form>}
 </section>;
}
