"""Autorizar manualmente la cuenta de la empresa. No envía correos."""
import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from modulos.gmail_api import ROOT, SCOPES, secret_path


def main():
    load_dotenv(ROOT / '.env')
    client_path = secret_path('GMAIL_CLIENT_SECRET_FILE', '.secrets/google-oauth-client.json')
    token_path = secret_path('GMAIL_TOKEN_FILE', '.secrets/gmail-token.json')
    if not client_path.is_file():
        raise SystemExit('Descargá el cliente OAuth de escritorio de Google Cloud y guardalo en .secrets/google-oauth-client.json, en la raíz del repositorio.')
    print('Autorizá únicamente la cuenta remitente indicada en GMAIL_FROM. Se solicitará permiso para enviar correos.')
    flow = InstalledAppFlow.from_client_secrets_file(str(client_path), SCOPES)
    credentials = flow.run_local_server(port=0, access_type='offline', prompt='consent', login_hint=os.getenv('GMAIL_FROM', ''))
    if not credentials.refresh_token or not credentials.has_scopes(SCOPES):
        raise SystemExit('No se recibió autorización persistente para enviar. Repetí el proceso.')
    token_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = token_path.with_name(token_path.name + '.tmp')
    descriptor = os.open(temp_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, 'w') as file:
        file.write(credentials.to_json())
    os.chmod(temp_path, 0o600)
    temp_path.replace(token_path)
    print('Autorización guardada. Reiniciá el backend. No se enviaron correos.')


if __name__ == '__main__':
    main()
