import json
import os
import requests

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def lambda_handler(event, context):
    print(f"[INFO] Notificar error - Event: {event}")
    for record in event.get('Records', []):
        if record.get('eventName') not in ['INSERT', 'MODIFY']:
            continue

        new_image = record['dynamodb'].get('NewImage', {})
        estado = new_image.get('estado', {}).get('S')
        device_id = new_image.get('device_id', {}).get('S')
        nombre = new_image.get('nombre', {}).get('S', '')
        ubicacion = new_image.get('ubicacion', {}).get('S', '')

        if estado == "error":
            mensaje = f"⚠️ Alerta: El dispositivo {nombre} (ID: {device_id}) en {ubicacion} presenta un ERROR. ¡Intervención requerida!"
            print(f"[INFO] Enviando alerta Telegram: {mensaje}")
            send_telegram(mensaje)

    return {"statusCode": 200, "body": "Processed"}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    try:
        r = requests.post(url, data=data)
        print(f"[INFO] Telegram response: {r.status_code}, {r.text}")
    except Exception as e:
        print(f"[ERROR] Error enviando mensaje Telegram: {e}")
