import json
import boto3
import os

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

def lambda_handler(event, context):
    print(f"[INFO] Eliminar dispositivo - Event: {event}")
    device_id = None
    timestamp = None
    username = None

    if 'pathParameters' in event and event['pathParameters']:
        device_id = event['pathParameters'].get('device_id')
    if event.get('body'):
        try:
            body = json.loads(event['body'])
            timestamp = body.get('timestamp')
            username = body.get('username')
        except Exception as e:
            print(f"[ERROR] Error parseando body: {e}")
            timestamp = None
            username = None

    if not device_id or not timestamp or not username:
        print("[WARN] Falta device_id, timestamp o username")
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': 'device_id, timestamp y username son requeridos'})
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

        table.delete_item(Key={'device_id': device_id, 'timestamp': timestamp})
        print(f"[INFO] Dispositivo eliminado: {device_id}, timestamp: {timestamp}, usuario: {username}")

        # Publicar evento en SQS
        if SQS_QUEUE_URL:
            try:
                sqs.send_message(
                    QueueUrl=SQS_QUEUE_URL,
                    MessageBody=json.dumps({
                        'event': 'delete_device',
                        'device_id': device_id,
                        'username': username,
                        'timestamp': timestamp
                    })
                )
                print("[INFO] Mensaje enviado a SQS")
            except Exception as sqs_err:
                print(f"[WARN] No se pudo enviar a SQS: {sqs_err}")

        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': 'Device deleted!', 'device_id': device_id, 'timestamp': timestamp})
        }
    except Exception as e:
        print(f"[ERROR] Error al eliminar dispositivo: {e}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
