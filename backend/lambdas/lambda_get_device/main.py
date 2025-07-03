import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def lambda_handler(event, context):
    device_id = None
    username = None
    timestamp = None

    if event.get("pathParameters"):
        device_id = event["pathParameters"].get("device_id")
    if event.get("queryStringParameters"):
        username = event["queryStringParameters"].get("username")
        timestamp = event["queryStringParameters"].get("timestamp")
    # Si viene directo
    if not device_id:
        device_id = event.get("device_id")
    if not username:
        username = event.get("username")
    if not timestamp:
        timestamp = event.get("timestamp", None)

    if not device_id or not username:
        return {'statusCode': 400, 'body': json.dumps({'error': 'device_id y username requeridos'})}

    # Busca SOLO si es del usuario
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
        return {'statusCode': 404, 'body': json.dumps({'error': 'Device not found'})}

    return {'statusCode': 200, 'body': json.dumps(item)}
