import smtplib
from email.message import EmailMessage

from config import RECIPIENTS, TXT_REPORT


def send_email():
    """Manda una mail."""
    msg = EmailMessage()
    msg['From'] = 'noreply@tuodominio.com'
    msg['To'] = ', '.join(RECIPIENTS)
    msg['Subject'] = 'Report vulnerabilità pom.xml'
    with open(TXT_REPORT) as f:
        body = f.read()
    msg.set_content(body)

    with smtplib.SMTP('localhost') as s:
        s.send_message(msg)
