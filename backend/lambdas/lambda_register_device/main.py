import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def lambda_handler(event, context):
    # Body puede ser string (por API Gateway)
    if 'body' in event and event['body']:
        try:
            payload = json.loads(event['body'])
        except Exception:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON'})
            }
    else:
        payload = event

    device_id = payload.get('device_id')
    nombre = payload.get('nombre', 'Dispositivo sin nombre')
    tipo = payload.get('tipo', 'generico')
    ubicacion = payload.get('ubicacion', 'no especificada')
    estado = payload.get('estado', 'activo')
    username = payload.get('username')  # <--- MULTIUSUARIO
    timestamp = datetime.utcnow().isoformat()

    if not device_id or not username:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'device_id y username requeridos'})
        }

    item = {
        'device_id': device_id,
        'timestamp': timestamp,
        'nombre': nombre,
        'tipo': tipo,
        'ubicacion': ubicacion,
        'estado': estado,
        'username': username,    # <--- MULTIUSUARIO
        'message': 'Device registered!'
    }
    table.put_item(Item=item)

    return {
        'statusCode': 200,
        'body': json.dumps(item)
    }
