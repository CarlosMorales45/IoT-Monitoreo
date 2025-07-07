import json
import os
import requests
import boto3

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
SQS_QUEUE_URL = os.environ.get('IOT_EVENTS_QUEUE_URL')  # <--- Variable de entorno correcta

# Cliente SQS (opcional, solo si la URL está configurada)
sqs = boto3.client('sqs') if SQS_QUEUE_URL else None

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

            # Publicar evento crítico en SQS
            if sqs and SQS_QUEUE_URL:
                try:
                    sqs.send_message(
                        QueueUrl=SQS_QUEUE_URL,
                        MessageBody=json.dumps({
                            'event': 'device_error',
                            'device_id': device_id,
                            'nombre': nombre,
                            'ubicacion': ubicacion,
                            'estado': estado
                        })
                    )
                    print("[INFO] Mensaje de error crítico enviado a SQS")
                except Exception as sqs_err:
                    print(f"[WARN] No se pudo enviar a SQS: {sqs_err}")

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
