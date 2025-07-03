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
    print(f"[INFO] Listar dispositivos - Event: {event}")
    username = None
    if 'body' in event and event['body']:
        try:
            body = json.loads(event['body'])
            username = body.get('username')
        except Exception as e:
            print(f"[WARN] No se pudo parsear el body: {e}")
    elif event.get('queryStringParameters'):
        username = event['queryStringParameters'].get('username')
    
    if not username:
        print("[WARN] Falta username para listar dispositivos")
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'username requerido'})
        }
    try:
        resp = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('username').eq(username)
        )
        items = resp.get('Items', [])
        print(f"[INFO] Dispositivos encontrados: {len(items)} para usuario {username}")
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps(items)
        }
    except Exception as e:
        print(f"[ERROR] Error al listar dispositivos: {e}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
