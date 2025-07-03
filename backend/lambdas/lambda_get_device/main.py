import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}

def lambda_handler(event, context):
    print(f"[INFO] Obtener dispositivo - Event: {event}")
    device_id = None
    username = None
    timestamp = None

    if event.get("pathParameters"):
        device_id = event["pathParameters"].get("device_id")
    if event.get("queryStringParameters"):
        username = event["queryStringParameters"].get("username")
        timestamp = event["queryStringParameters"].get("timestamp")
    if not device_id:
        device_id = event.get("device_id")
    if not username:
        username = event.get("username")
    if not timestamp:
        timestamp = event.get("timestamp", None)

    if not device_id or not username:
        print("[WARN] Falta device_id o username")
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'device_id y username requeridos'})
        }

    try:
        key = {'device_id': device_id}
        if timestamp:
            key['timestamp'] = timestamp
            response = table.get_item(Key=key)
            item = response.get('Item')
            if item and item.get('username') != username:
                item = None
        else:
            from boto3.dynamodb.conditions import Key as KeyCond, Attr
            response = table.query(
                KeyConditionExpression=KeyCond('device_id').eq(device_id),
                FilterExpression=Attr('username').eq(username),
                ScanIndexForward=False,
                Limit=1
            )
            items = response.get('Items', [])
            item = items[0] if items else None

        if not item:
            print(f"[WARN] Dispositivo no encontrado: {device_id}, usuario: {username}")
            return {
                'statusCode': 404,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Device not found'})
            }
        print(f"[INFO] Dispositivo encontrado: {item}")
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps(item)
        }
    except Exception as e:
        print(f"[ERROR] Error al obtener dispositivo: {e}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
