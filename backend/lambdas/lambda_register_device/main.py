import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def lambda_handler(event, context):
    device_id = event.get('device_id')
    nombre = event.get('nombre', 'Dispositivo sin nombre')
    tipo = event.get('tipo', 'generico')
    ubicacion = event.get('ubicacion', 'no especificada')
    estado = event.get('estado', 'activo')
    timestamp = datetime.utcnow().isoformat()

    item = {
        'device_id': device_id,
        'timestamp': timestamp,
        'nombre': nombre,
        'tipo': tipo,
        'ubicacion': ubicacion,
        'estado': estado,
        'message': 'Device registered!'
    }
    table.put_item(Item=item)

    return {
        'statusCode': 200,
        'body': json.dumps(item)
    }
