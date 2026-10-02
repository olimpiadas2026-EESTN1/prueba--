import os
import unittest
from unittest.mock import AsyncMock, patch

import correo


class CorreoRegistroTests(unittest.IsolatedAsyncioTestCase):
    async def test_sin_dominio_verificado_usa_smtp(self):
        entorno = {
            "RESEND_API_KEY": "re_prueba",
            "MAIL_USERNAME": "cuenta@example.test",
            "MAIL_PASSWORD": "secreto",
        }
        with patch.dict(os.environ, entorno, clear=True), patch(
            "correo.asyncio.to_thread", new_callable=AsyncMock
        ) as to_thread:
            resultado = await correo.enviar_correo_registro(
                "usuario@example.test", "Usuario"
            )

        self.assertEqual(resultado["provider"], "smtp")
        to_thread.assert_awaited_once()

    async def test_dominio_verificado_usa_resend(self):
        entorno = {
            "RESEND_API_KEY": "re_prueba",
            "RESEND_FROM": "AirTrip <noreply@airtrip.example>",
        }
        with patch.dict(os.environ, entorno, clear=True), patch(
            "correo._enviar_resend", new_callable=AsyncMock, return_value={"id": "mail_1"}
        ) as enviar:
            resultado = await correo.enviar_correo_registro(
                "usuario@example.test", "Usuario"
            )

        self.assertEqual(resultado["id"], "mail_1")
        enviar.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
