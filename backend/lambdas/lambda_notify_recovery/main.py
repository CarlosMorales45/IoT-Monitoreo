import json
import os
import requests

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def lambda_handler(event, context):
    for record in event.get('Records', []):
        if record.get('eventName') not in ['INSERT', 'MODIFY']:
            continue

        new_image = record['dynamodb'].get('NewImage', {})
        old_image = record['dynamodb'].get('OldImage', {})
        estado_nuevo = new_image.get('estado', {}).get('S')
        estado_antiguo = old_image.get('estado', {}).get('S')
        device_id = new_image.get('device_id', {}).get('S')
        nombre = new_image.get('nombre', {}).get('S', '')
        ubicacion = new_image.get('ubicacion', {}).get('S', '')

        # Notificar si el estado pasa a "activo" y antes no era "activo"
        if estado_nuevo == "activo" and estado_antiguo != "activo":
            mensaje = f"✅ Info: El dispositivo {nombre} (ID: {device_id}) en {ubicacion} se ha RECUPERADO y está activo."
            send_telegram(mensaje)

    return {"statusCode": 200, "body": "Processed"}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)
