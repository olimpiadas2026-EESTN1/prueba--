import { useEffect, useRef, useState } from 'react';
import { useAdmin } from './useAdmin';
const entities = [['resumen','Resumen'],['usuarios','Usuarios'],['pedidos','Pedidos'],['ventas','Ventas'],['viajes','Vuelos y micros'],['paquetes','Paquetes'],['autos','Autos'],['auditoria','Cambios'],['correos','Correos de compra']];
const fields = {usuarios:['nombre','apellido','correo_electronico'], viajes:['nombre','descripcion','precio','cupos','estado'], paquetes:['nombre','descripcion','precio','cupos','estado'], autos:['modelo','disponibles','precio_por_dia']};
const keys = {usuarios:'id',pedidos:'id',ventas:'id',viajes:'codigo',paquetes:'codigo',autos:'auto_id'};
function Cell({ value }) { return typeof value === 'object' && value !== null ? <details><summary>Ver detalle</summary><pre>{JSON.stringify(value,null,2)}</pre></details> : String(value ?? '—'); }
function Table({ rows, onUser, onEdit, onDelete, busy }) {
 if (!rows.length) return <p>No hay registros.</p>;
 const cols=Object.keys(rows[0]);
 return <div className="admin-table"><table><thead><tr>{cols.map(k=><th key={k}>{k.replaceAll('_',' ')}</th>)}{(onUser||onEdit||onDelete)&&<th>Acciones</th>}</tr></thead><tbody>{rows.map((row,i)=><tr key={row.id ?? i}>{cols.map(k=><td key={k}><Cell value={row[k]}/></td>)}{(onUser||onEdit||onDelete)&&<td>{onUser&&(row.uc_id||row.email)&&<button onClick={()=>onUser(row.uc_id ?? row.id)}>Ver cuenta e historial</button>}{onEdit&&!row.eliminado_en&&<button disabled={busy} onClick={()=>onEdit(row)}>Editar</button>}{onDelete&&<button disabled={busy} onClick={()=>onDelete(row)}>{row.eliminado_en ? "Restaurar" : "Eliminar"}</button>}</td>}</tr>)}</tbody></table></div>;
}
export default function Gestion({ revision }) {
 const { request }=useAdmin();
 const [section,setSection]=useState('resumen');
 const confirmationRef=useRef(null);
 const [trash,setTrash]=useState(false); const [removal,setRemoval]=useState(null);
 const [query,setQuery]=useState(''); const [search,setSearch]=useState('');
 const [data,setData]=useState(null); const [error,setError]=useState('');
 const [orderEdit,setOrderEdit]=useState(null); const [history,setHistory]=useState([]);
 const [profile,setProfile]=useState(null); const [edit,setEdit]=useState(null);
 useEffect(()=>{if(removal)confirmationRef.current?.scrollIntoView({behavior:'smooth',block:'center'});},[removal]);
 const [version,setVersion]=useState(0); const [busy,setBusy]=useState(false);
 useEffect(()=>{
  let active=true; setData(null); setError(''); setProfile(null); setEdit(null); setOrderEdit(null); setRemoval(null);
  const path=['resumen','usuarios','pedidos','ventas','auditoria','correos'].includes(section)?`/admin/${section}`:`/admin/catalogo/${section}`;
  request(path+`?eliminados=${trash}`+(section==='usuarios'?`&q=${encodeURIComponent(search)}`:'')).then(d=>{if(active)setData(d);}).catch(e=>{if(active)setError(e.message);});
  return ()=>{active=false;};
  // eslint-disable-next-line react-hooks/exhaustive-deps
 },[section,search,version,revision,trash]);
 async function showUser(id) {setError('');try {setProfile(await request(`/admin/usuarios/${id}`));} catch(e){setError(e.message);}}
 async function retryMail(id) {
  setBusy(true);setError('');
  try {await request(`/admin/correos/${id}/reintentar`,{method:'POST'});setVersion(v=>v+1);}catch(e){setError(e.message);}finally{setBusy(false);}
 }
 async function verifyPayment(event) {
  event.preventDefault();const id=new FormData(event.currentTarget).get('payment_id');setBusy(true);setError('');
  try {const result=await request(`/admin/pagos/${id}/verificar`,{method:'POST'});if(result.confirmado)setVersion(v=>v+1);else setError('El pago aún no está aprobado o no corresponde a un pedido de esta tienda.');}catch(e){setError(e.message);}finally{setBusy(false);}
 }
 async function editOrder(order) {
  setError('');setHistory([]);setOrderEdit(order);
  try {setHistory(await request(`/admin/pedidos/${order.id}/historial`));}catch(e){setError(e.message);}
 }
 async function saveOrder(event) {
  event.preventDefault();setBusy(true);setError('');
  const values=Object.fromEntries(new FormData(event.currentTarget));
  try {await request(`/admin/pedidos/${orderEdit.id}/estado`,{method:'PATCH',body:JSON.stringify({...values,estado_esperado:orderEdit.estado_gestion})});setOrderEdit(null);setVersion(v=>v+1);}catch(e){setError(e.message);}finally{setBusy(false);}
 }
 async function confirmRemoval(event) {
  event.preventDefault();setBusy(true);setError('');
  const motivo=new FormData(event.currentTarget).get('motivo');
  const restoring=Boolean(removal.row.eliminado_en);
  try {
   await request(`/admin/datos/${removal.section}/${removal.row[keys[removal.section]]}${restoring?'/restaurar':''}`,{method:restoring?'POST':'DELETE',body:JSON.stringify({motivo})});
   setRemoval(null);setVersion(v=>v+1);
  }catch(e){setError(e.message);}finally{setBusy(false);}
 }
 async function save(event) {
  event.preventDefault();setBusy(true);setError('');
  const values=Object.fromEntries(new FormData(event.currentTarget));
  for(const k of ['precio','cupos','disponibles','precio_por_dia'])if(k in values)values[k]=Number(values[k]);
  try {await request(`/admin/datos/${section}/${edit[keys[section]]}`,{method:'PATCH',body:JSON.stringify(values)});setEdit(null);setVersion(v=>v+1);}catch(e){setError(e.message);}finally{setBusy(false);}
 }
 return <section aria-label="Gestión de la empresa">
  <nav className="admin-tabs" aria-label="Gestión">{entities.map(([key,label])=><button key={key} aria-pressed={section===key} disabled={busy} onClick={()=>{setSection(key);setTrash(false);setRemoval(null);}}>{label}</button>)}</nav>
  <h2>{entities.find(([k])=>k===section)[1]}</h2>
  <button disabled={busy} onClick={()=>setVersion(v=>v+1)}>Actualizar datos</button>
  {keys[section]&&<label><input type="checkbox" checked={trash} disabled={busy} onChange={e=>setTrash(e.target.checked)}/> Ver papelera</label>}
  {section==='resumen'&&<p>El total de ventas incluye las enviadas a la papelera: eliminarlas no anula el cobro.</p>}
  {section==='usuarios'&&<form onSubmit={e=>{e.preventDefault();setSearch(query);}} className="admin-search"><label>Buscar por nombre o correo <input value={query} onChange={e=>setQuery(e.target.value)}/></label><button>Buscar</button></form>}
  {error&&<p role="alert">{error}</p>}
  {!data&&!error&&<p role="status">Cargando datos de la base…</p>}
  {data&&(section==='resumen'?<div className="admin-stats">{Object.entries(data).map(([k,v])=><article key={k}><h3>{k.replaceAll('_',' ')}</h3><strong>{v}</strong></article>)}</div>:<><p>Hasta 200 registros recientes. Los pedidos pendientes no se contabilizan como ventas.</p><Table rows={data} onUser={['usuarios','pedidos','ventas'].includes(section)?showUser:null} onEdit={section==='pedidos'?editOrder:fields[section]?setEdit:null} busy={busy} onDelete={keys[section]?row=>{setEdit(null);setOrderEdit(null);setRemoval({row,section});}:null}/></>)}
  {removal&&<form ref={confirmationRef} className="admin-form" onSubmit={confirmRemoval} aria-label="Confirmar eliminación o restauración"><h3>{removal.row.eliminado_en?'Restaurar':'Eliminar'} {entities.find(([key])=>key===removal.section)?.[1]} #{removal.row[keys[removal.section]]}</h3><p>{removal.row.eliminado_en?'El registro volverá a la lista activa.':'El registro se enviará a la papelera y podrás restaurarlo. No se eliminarán los registros relacionados.'}</p>{removal.section==='usuarios'&&<p>Eliminar la cuenta bloquea su acceso. Restaurarla permite iniciar sesión nuevamente con su contraseña.</p>}{['pedidos','ventas'].includes(removal.section)&&<p>Esta acción no cancela pagos, no devuelve dinero ni repone cupos. Los pagos pendientes todavía pueden confirmarse.</p>}<label>Motivo<input name="motivo" required maxLength={500}/></label><button disabled={busy}>{busy?'Guardando…':removal.row.eliminado_en?'Confirmar restauración':'Confirmar eliminación'}</button><button type="button" disabled={busy} onClick={()=>setRemoval(null)}>Cancelar</button></form>}
  {section==='correos' &&Array.isArray(data)&&data.filter(mail=>mail.estado!=='enviado').map(mail=><button disabled={busy} key={`${mail.pedido_id}-${mail.tipo}`} onClick={()=>retryMail(mail.pedido_id)}>Reintentar pendientes del pedido {mail.pedido_id}</button>)}
  {section==='pedidos'&&<form className="admin-form" onSubmit={verifyPayment}><label>ID de pago de Mercado Pago<input name="payment_id" inputMode="numeric" pattern="[0-9]+" required /></label><button disabled={busy}>Verificar pago y preparar comprobante</button></form>}
  {orderEdit&&section==='pedidos'&&<form className="admin-form" onSubmit={saveOrder}><h3>Gestionar pedido {orderEdit.id}</h3><p>Pago: {orderEdit.estado}. Gestión actual: {orderEdit.estado_gestion}. El cambio no cobra ni devuelve dinero.</p><label>Nuevo estado<select name="estado" required defaultValue=""><option value="" disabled>Seleccioná un estado</option>{({pendiente:['en_preparacion','en_revision'],en_preparacion:['listo','en_revision'],listo:['en_revision'],completado:[],en_revision:['pendiente','en_preparacion','listo']}[orderEdit.estado_gestion]||[]).filter(s=>orderEdit.estado==='confirmado'||['pendiente','en_revision'].includes(s)).map(s=><option key={s} value={s}>{s.replaceAll('_',' ')}</option>)}</select></label><label>Motivo del cambio<input name="motivo" required maxLength={500}/></label><button disabled={busy}>Guardar estado</button><button type="button" onClick={()=>setOrderEdit(null)}>Cerrar</button><h4>Historial de cambios</h4><Table rows={history}/></form>}
  {profile&&<section className="admin-detail"><button onClick={()=>setProfile(null)}>Cerrar ficha</button><h2>Cuenta de {profile.usuario.nombre} {profile.usuario.apellido}</h2><p>Usuario #{profile.usuario.id} · {profile.usuario.email}</p><h3>Historial de pedidos</h3><Table rows={profile.pedidos}/><h3>Historial de ventas registradas</h3><Table rows={profile.ventas}/></section>}
  {edit&&<form className="admin-form" onSubmit={save}><h3>Editar registro #{edit[keys[section]]}</h3>{fields[section].map(f=><label key={f}>{f.replaceAll('_',' ')}{f==='estado'?<select name={f} defaultValue={edit[f]}><option>Disponible</option><option>No disponible</option></select>:<input required name={f} defaultValue={edit[f]??(f==='correo_electronico'?edit.email:'')} type={['precio','cupos','disponibles','precio_por_dia'].includes(f)?'number':f==='correo_electronico'?'email':'text'} min="0" step={f.includes('precio')?'0.01':'1'}/>}</label>)}<button disabled={busy}>{busy?'Guardando…':'Guardar cambios'}</button><button type="button" onClick={()=>setEdit(null)}>Cancelar</button></form>}
 </section>;
}
