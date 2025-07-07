import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

# Cliente SQS
sqs = boto3.client('sqs')
SQS_QUEUE_URL = os.environ.get('IOT_EVENTS_QUEUE_URL')

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
    print(f"[INFO] Actualizar dispositivo - Event: {event}")
    path_params = event.get("pathParameters") or {}
    device_id = path_params.get("device_id")
    username = None

    try:
        body = json.loads(event.get("body") or "{}")
        username = body.get("username")
    except Exception as e:
        print(f"[WARN] No se pudo parsear el body: {e}")
        body = {}
        username = None

    timestamp = body.get("timestamp")
    update_fields = body.get("update_fields", {})

    if not device_id or not timestamp or not update_fields or not username:
        print("[WARN] Faltan datos obligatorios para actualizar")
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'device_id, timestamp, update_fields y username son requeridos'})
        }

    try:
        resp = table.get_item(Key={'device_id': device_id, 'timestamp': timestamp})
        item = resp.get('Item')
        if not item or item.get('username') != username:
            print(f"[WARN] No autorizado o dispositivo no encontrado: {device_id}, {timestamp}, {username}")
            return {
                'statusCode': 404,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'No autorizado o dispositivo no encontrado'})
            }

        update_expr = []
        expr_attr_values = {}
        expr_attr_names = {}
        for k, v in update_fields.items():
            update_expr.append(f"#{k} = :{k}")
            expr_attr_values[f":{k}"] = v
            expr_attr_names[f"#{k}"] = k

        response = table.update_item(
            Key={'device_id': device_id, 'timestamp': timestamp},
            UpdateExpression="SET " + ", ".join(update_expr),
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            ReturnValues="ALL_NEW"
        )
        updated = response.get('Attributes', {})
        print(f"[INFO] Dispositivo actualizado: {updated}")

        # Publicar evento en SQS (usando función estandarizada)
        send_event_to_sqs('update_device', {
            'device_id': device_id,
            'username': username,
            'timestamp': timestamp,
            'update_fields': update_fields
        })

        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps(updated)
        }
    except Exception as e:
        print(f"[ERROR] Error al actualizar dispositivo: {e}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
