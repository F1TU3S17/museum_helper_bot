from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiosmtplib import SMTP
import asyncio

EMAIL = 'kamenykakamensky@yandex.ru'
PWD = 'loeoldilpnfzrhqw'

async def send_mail(msg):
    message = MIMEMultipart()
    message["From"] = EMAIL
    message["To"] = EMAIL
    message["Subject"] = "Сообщение из телеграмм-бота"
    message.attach(MIMEText(f"<html><body>{msg}</body></html>", "html", "utf-8"))

    smtp_client = SMTP(hostname="smtp.yandex.ru", port=465, use_tls=True)
    async with smtp_client:
        await smtp_client.login(EMAIL, PWD)
        await smtp_client.send_message(message)

#asyncio.run(send_mail('Привет'))