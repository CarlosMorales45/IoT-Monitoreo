import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def lambda_handler(event, context):
    device_id = event.get('device_id')
    timestamp = event.get('timestamp', None)

    if not device_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'device_id is required'})
        }

    # Si envías un timestamp puedes buscar un ítem único, si no, consulta por device_id (trae el último, si hay varios)
    key = {'device_id': device_id}
    if timestamp:
        key['timestamp'] = timestamp
        response = table.get_item(Key=key)
        item = response.get('Item')
    else:
        # Si solo tienes device_id, busca todos los items con ese ID (puede haber varios si hay varios registros con diferentes timestamp)
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('device_id').eq(device_id),
            ScanIndexForward=False,  # Orden descendente por timestamp
            Limit=1  # Solo el más reciente
        )
        items = response.get('Items', [])
        item = items[0] if items else None

    if not item:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Device not found'})
        }

    return {
        'statusCode': 200,
        'body': json.dumps(item)
    }
