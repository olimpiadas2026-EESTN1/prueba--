import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { API_URL, apiFetch } from '../api';
import './mis-pedidos.css';
const labels={creado:'Pendiente de pago',pendiente_pago:'Pago iniciado',error_checkout:'Pago a revisar',confirmado:'Pago confirmado',pendiente:'Pendiente de entrega',en_preparacion:'En preparación',listo:'Listo para entregar',completado:'Entregado',en_revision:'En revisión'};
export default function MisPedidos(){
 const [orders,setOrders]=useState(null),[requests,setRequests]=useState([]),[error,setError]=useState(''),[version,setVersion]=useState(0),[filter,setFilter]=useState('pendientes'),[action,setAction]=useState(null),[busy,setBusy]=useState(false);
 const token=sessionStorage.getItem('buyer_token');
 const call=async(path,options={})=>(await apiFetch(`${API_URL}${path}`,{...options,headers:{'Content-Type':'application/json',Authorization:`Bearer ${token}`}})).json();
 useEffect(()=>{
  let active=true;setOrders(null);setError('');setAction(null);
  if(token) Promise.all([call('/clientes/mis-pedidos'),call('/clientes/solicitudes')]).then(([d,r])=>{if(active){setOrders(d);setRequests(r);}}).catch(e=>{if(active)setError(e.message);});
  return ()=>{active=false;};
  // eslint-disable-next-line react-hooks/exhaustive-deps
 },[token,version]);
 async function pay(order){setBusy(true);setError('');try{const r=await call(`/clientes/pedidos/${order.id}/pagar`,{method:'POST'});window.location.assign(r.init_point);}catch(e){setError(e.message);setVersion(v=>v+1);window.alert(e.message);}finally{setBusy(false);}}
 async function save(e){e.preventDefault();setBusy(true);setError('');const f=new FormData(e.currentTarget);try{
  const base=`/clientes/pedidos/${action.order.id}`;
  if(action.type==='editar'){
    const items=action.order.items.map((i,n)=>({id:i.id,tipo:i.tipo,quantity:Number(f.get(`q${n}`)),...(i.tipo==='auto'?{fecha_retiro:i.fecha_retiro,fecha_devolucion:i.fecha_devolucion}:{})})).filter(i=>i.quantity>0);
   if(!items.length)throw new Error('Para quitar todos los artículos, usá Anular pedido.');
   await call(base,{method:'PATCH',body:JSON.stringify({items,version:action.order.version})});
  }else if(action.type==='anular')await call(base+'/anular',{method:'POST',body:JSON.stringify({motivo:f.get('detalle')})});
  else await call(base+'/solicitudes',{method:'POST',body:JSON.stringify({tipo:f.get('tipo'),detalle:f.get('detalle')})});
  setVersion(v=>v+1);
 }catch(err){setError(err.message);}finally{setBusy(false);}}
 const visible=orders?.filter(o=>filter==='todos'||(filter==='pendientes'?!o.anulado_en&&o.estado_gestion!=='completado':filter==='entregados'?o.estado_gestion==='completado':Boolean(o.anulado_en)));
 return <section className="mis-pedidos"><h1>Mis pedidos</h1><p>Registrá tu pedido, revisá cantidades y luego elegí Pagar. Iniciar el pago bloquea la edición directa; ventas atiende los cambios posteriores. <Link to="/ayuda">Ayuda</Link></p>
 {!token?<p><Link to="/login">Iniciá sesión</Link> para consultar tus pedidos.</p>:<>
 <button disabled={busy} onClick={()=>setVersion(v=>v+1)}>Actualizar pedidos</button><label> Mostrar <select value={filter} onChange={e=>setFilter(e.target.value)}><option value="pendientes">Pendientes de entrega</option><option value="entregados">Entregados</option><option value="anulados">Anulados</option><option value="todos">Todos</option></select></label>
 {error&&<p role="alert">{error}</p>}{!orders&&!error&&<p role="status">Cargando pedidos…</p>}{visible?.length===0&&<p>No hay pedidos en esta vista. <Link to="/productos">Ver lista de productos</Link></p>}
 {visible?.map(order=><article key={order.id}><h2>Pedido {order.id}</h2><p>{new Date(order.creado_en).toLocaleString('es-AR')}</p><p><strong>Pago:</strong> {labels[order.estado]||order.estado}</p><p><strong>Gestión:</strong> {order.anulado_en?'Anulado':labels[order.estado_gestion]||order.estado_gestion}</p><ul>{order.items.map((item,i)=><li key={i}>{item.title} × {item.quantity}{item.tipo==='auto'&&item.fecha_retiro&&item.fecha_devolucion?<span> · Retiro {item.fecha_retiro} · devolución {item.fecha_devolucion} · {new Intl.NumberFormat('es-AR',{style:'currency',currency:order.moneda||'ARS'}).format(item.precio_diario)} por día</span>:null}</li>)}</ul><strong>{new Intl.NumberFormat('es-AR',{style:'currency',currency:order.moneda||'ARS'}).format(order.total)}</strong>
 {!order.anulado_en&&order.estado_gestion!=='completado'&&<div>
 {order.estado!=='confirmado'&&<button disabled={busy||order.estado==='error_checkout'} onClick={()=>pay(order)}>Pagar con Mercado Pago</button>}
 {!order.checkout_iniciado&&['pendiente','en_revision'].includes(order.estado_gestion)?<><button disabled={busy} onClick={()=>setAction({order,type:'editar'})}>Modificar cantidades</button><button disabled={busy} onClick={()=>setAction({order,type:'anular'})}>Anular pedido</button></>:<button disabled={busy} onClick={()=>setAction({order,type:'solicitar'})}>Solicitar cambio o anulación</button>}
 </div>}
 {action?.order.id===order.id&&<form onSubmit={save}><h3>{action.type==='editar'?'Modificar pedido':action.type==='anular'?'Confirmar anulación':'Solicitud a ventas'}</h3>{action.type==='editar'?<><p>Cantidad 0 quita el artículo. Se recalculan los precios con el catálogo actual.</p>{order.items.map((i,n)=><label key={n}>{i.title}<input type="number" name={`q${n}`} min="0" max="50" required defaultValue={i.quantity}/></label>)}</>:<>{action.type==='solicitar'&&<label>Tipo<select name="tipo"><option value="modificacion">Modificación</option><option value="anulacion">Anulación</option></select></label>}<label>Motivo o detalle<textarea name="detalle" required maxLength={1000}/></label></>}<button disabled={busy}>Confirmar</button><button type="button" disabled={busy} onClick={()=>setAction(null)}>Cerrar</button></form>}
 {requests.filter(r=>r.pedido_id===order.id).map(r=><p key={r.id}>Solicitud de {r.tipo}: {r.estado}. {r.respuesta||'Pendiente de respuesta de ventas.'}</p>)}
 </article>)}
 </>}
 </section>;
}
