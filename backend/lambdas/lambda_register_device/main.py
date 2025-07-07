import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

sqs = boto3.client('sqs')
SQS_QUEUE_URL = os.environ.get('IOT_EVENTS_QUEUE_URL')  # ← Corrección aquí

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}

def send_event_to_sqs(event_type, payload):
    if not SQS_QUEUE_URL:
        print("[WARN] SQS_QUEUE_URL no configurado")
        return
    try:
        message = {
            'event_type': event_type,
            'payload': payload,
            'timestamp': datetime.utcnow().isoformat()
        }
        response = sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message)
        )
        print(f"[INFO] Evento enviado a SQS: {response.get('MessageId')}")
    except Exception as e:
        print(f"[ERROR] No se pudo enviar mensaje a SQS: {e}")

def lambda_handler(event, context):
    print(f"[INFO] Registrar dispositivo - Event: {event}")
    if 'body' in event and event['body']:
        try:
            payload = json.loads(event['body'])
        except Exception as e:
            print(f"[ERROR] JSON inválido: {e}")
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Invalid JSON'})
            }
    else:
        payload = event

    device_id = payload.get('device_id')
    nombre = payload.get('nombre', 'Dispositivo sin nombre')
    tipo = payload.get('tipo', 'generico')
    ubicacion = payload.get('ubicacion', 'no especificada')
    estado = payload.get('estado', 'activo')
    username = payload.get('username')
    timestamp = datetime.utcnow().isoformat()

    if not device_id or not username:
        print("[WARN] Faltan datos obligatorios (device_id o username)")
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'device_id y username requeridos'})
        }

    item = {
        'device_id': device_id,
        'timestamp': timestamp,
        'nombre': nombre,
        'tipo': tipo,
        'ubicacion': ubicacion,
        'estado': estado,
        'username': username,
        'message': 'Device registered!'
    }
    try:
        table.put_item(Item=item)
        print(f"[INFO] Dispositivo registrado: {item}")
        # Enviar evento a SQS
        send_event_to_sqs('register_device', item)
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps(item)
        }
    except Exception as e:
        print(f"[ERROR] Error al registrar dispositivo: {e}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
