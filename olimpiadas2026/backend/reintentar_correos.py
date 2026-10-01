"""Reintenta comprobantes confirmados pendientes; no genera compras ni pagos."""
import main  # carga .env
from modulos.gestion import query
from modulos.correos import deliver

if __name__=='__main__':
    rows=query("SELECT DISTINCT pedido_id FROM correos_compra WHERE estado<>'enviado' ORDER BY pedido_id LIMIT 100")
    for row in rows:
        print(row['pedido_id'],deliver(str(row['pedido_id'])))
