"""Envío mediante Gmail API con OAuth y permiso exclusivo gmail.send."""
import os
import base64
from pathlib import Path
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
ROOT = Path(os.getenv('APP_ROOT', Path(__file__).resolve().parents[1]))


def secret_path(variable, default):
    path = Path(os.getenv(variable, default)).expanduser()
    return path if path.is_absolute() else ROOT / path


def gmail_credentials():
    path = secret_path('GMAIL_TOKEN_FILE', '.secrets/gmail-token.json')
    if not path.is_file():
        raise RuntimeError('Falta autorizar Gmail: ejecutar autorizar_gmail.py')
    credentials = Credentials.from_authorized_user_file(str(path), SCOPES)
    if not credentials.has_scopes(SCOPES):
        raise RuntimeError('Falta el permiso gmail.send')
    if not credentials.valid:
        if not credentials.refresh_token:
            raise RuntimeError('Volvé a autorizar la cuenta remitente')
        credentials.refresh(Request())
    return credentials


def send_email(recipient, subject, body, message_id):
    sender = os.getenv('GMAIL_FROM', '').strip()
    if not sender or '@' not in sender:
        raise RuntimeError('Falta configurar GMAIL_FROM')
    message = EmailMessage()
    message['From'] = sender
    message['To'] = recipient
    message['Subject'] = subject
    message['Message-ID'] = message_id
    message.set_content(body)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('ascii')
    with build('gmail', 'v1', credentials=gmail_credentials(), cache_discovery=False) as service:
        result = service.users().messages().send(userId='me', body={'raw': raw}).execute(num_retries=0)
    if not result.get('id'):
        raise RuntimeError('Gmail no confirmó la aceptación del mensaje')
    return result['id']
