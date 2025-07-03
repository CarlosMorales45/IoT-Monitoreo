import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def lambda_handler(event, context):
    username = None
    # Por API Gateway: body o queryStringParameters
    if 'body' in event and event['body']:
        try:
            body = json.loads(event['body'])
            username = body.get('username')
        except Exception:
            pass
    elif event.get('queryStringParameters'):
        username = event['queryStringParameters'].get('username')
    
    if not username:
        return {'statusCode': 400, 'body': json.dumps({'error': 'username requerido'})}
    # Busca SOLO los dispositivos de ese usuario
    try:
        resp = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('username').eq(username)
        )
        items = resp.get('Items', [])
        return {'statusCode': 200, 'body': json.dumps(items)}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
