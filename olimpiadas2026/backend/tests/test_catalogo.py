import unittest
from types import SimpleNamespace
from unittest.mock import patch,MagicMock
from fastapi import HTTPException
from pydantic import ValidationError
import main
from modulos import autos,excursiones,vinculos_catalogo
from modulos.esquemas import Auto,Auto_id
from controladores.date import convertirDate,convertirHora

class CatalogoTests(unittest.TestCase):
    def test_invalid_price_stock_id(self):
        for price,stock in [(0,1),(-1,1),(float('inf'),1),(100,-1)]:
            with self.assertRaises(ValidationError): Auto(modelo='Demo',disponibles=stock,precio_por_dia=price)
        with self.assertRaises(ValidationError): Auto_id(auto_id=0)
    def test_invalid_dates(self):
        for fn,value in [(convertirDate,'31/02/26'),(convertirHora,'25:30')]:
            with self.assertRaises(HTTPException) as error: fn(value)
            self.assertEqual(error.exception.status_code,422)
    def test_missing_details(self):
        for module,fn,data in [(autos,autos.verAutoID,SimpleNamespace(auto_id=1)),(excursiones,excursiones.buscarExcursionporId,SimpleNamespace(excursion_id=1))]:
            with patch.object(module,'query',return_value=[]),self.assertRaises(HTTPException) as error: fn(data)
            self.assertEqual(error.exception.status_code,404)
    def test_relations_preserve_contract_single_query(self):
        with patch.object(excursiones,'query',return_value=[{'Nombre':'Demo'}]) as q:
            self.assertEqual(excursiones.verExcursionPaquete(SimpleNamespace(pv_id=1)),[[{'Nombre':'Demo'}]])
            q.assert_called_once()
        with patch.object(autos,'query',return_value=[{'modelo':'Demo'}]) as q:
            self.assertEqual(autos.verAutoPV(SimpleNamespace(pv_id=1)),[{'modelo':'Demo'}])
            q.assert_called_once()
    def test_link_missing_parent(self):
        conn=MagicMock();cur=conn.__enter__.return_value.cursor.return_value.__enter__.return_value
        cur.fetchone.return_value=None
        with patch.object(vinculos_catalogo,'connection',return_value=conn),self.assertRaises(HTTPException): vinculos_catalogo.vincular('vs_at',1,2)
        self.assertEqual(cur.execute.call_count,1)
    def test_link_avoids_duplicates_and_default_sequence(self):
        conn=MagicMock();cur=conn.__enter__.return_value.cursor.return_value.__enter__.return_value
        cur.fetchone.return_value=(1,)
        with patch.object(vinculos_catalogo,'connection',return_value=conn): vinculos_catalogo.vincular('pv_exc',1,2)
        statement=cur.execute.call_args.args[0].as_string()
        self.assertIn('NOT EXISTS',statement)
        self.assertIn('MAX(id)',statement)
        self.assertEqual(cur.execute.call_args.args[1],(1,2,1,2))
