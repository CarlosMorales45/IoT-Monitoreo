import json
import os
import requests
import boto3

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
SQS_QUEUE_URL = os.environ.get('IOT_EVENTS_QUEUE_URL')  # <- Variable correcta

sqs = boto3.client('sqs') if SQS_QUEUE_URL else None

def lambda_handler(event, context):
    print(f"[INFO] Notificar recuperación - Event: {event}")
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

        if estado_nuevo == "activo" and estado_antiguo != "activo":
            mensaje = f"✅ Info: El dispositivo {nombre} (ID: {device_id}) en {ubicacion} se ha RECUPERADO y está activo."
            print(f"[INFO] Enviando mensaje de recuperación: {mensaje}")
            send_telegram(mensaje)

            # Publicar evento de recuperación en SQS
            if sqs and SQS_QUEUE_URL:
                try:
                    sqs.send_message(
                        QueueUrl=SQS_QUEUE_URL,
                        MessageBody=json.dumps({
                            'event': 'device_recovery',
                            'device_id': device_id,
                            'nombre': nombre,
                            'ubicacion': ubicacion,
                            'estado': estado_nuevo
                        })
                    )
                    print("[INFO] Mensaje de recuperación enviado a SQS")
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
