import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def lambda_handler(event, context):
    device_id = event.get('device_id')
    timestamp = event.get('timestamp')

    if not device_id or not timestamp:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'device_id y timestamp son requeridos'})
        }

    response = table.delete_item(
        Key={
            'device_id': device_id,
            'timestamp': timestamp
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Device deleted!', 'device_id': device_id, 'timestamp': timestamp})
    }
