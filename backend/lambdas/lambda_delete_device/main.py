import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def lambda_handler(event, context):
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
        except Exception:
            timestamp = None
            username = None

    if not device_id or not timestamp or not username:
        return {'statusCode': 400, 'body': json.dumps({'message': 'device_id, timestamp y username son requeridos'})}

    # Verifica que sea del usuario
    resp = table.get_item(Key={'device_id': device_id, 'timestamp': timestamp})
    item = resp.get('Item')
    if not item or item.get('username') != username:
        return {'statusCode': 404, 'body': json.dumps({'error': 'No autorizado o dispositivo no encontrado'})}

    response = table.delete_item(Key={'device_id': device_id, 'timestamp': timestamp})

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Device deleted!', 'device_id': device_id, 'timestamp': timestamp})
    }
