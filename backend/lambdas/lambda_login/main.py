import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['USERS_TABLE_NAME'])

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}

def lambda_handler(event, context):
    print(f"[INFO] Intento de login - Event: {event}")
    try:
        body = event.get('body')
        if body:
            body = json.loads(body)
        else:
            body = event
        username = body.get('username')
        password = body.get('password')

        if not username or not password:
            print("[WARN] Faltan username o password en login")
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'username y password requeridos'})
            }

        response = table.get_item(Key={'username': username})
        user = response.get('Item')
        if not user or user.get('password') != password:
            print(f"[WARN] Credenciales inválidas para usuario: {username}")
            return {
                'statusCode': 401,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Credenciales inválidas'})
            }

        print(f"[INFO] Login exitoso para usuario: {username}")
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': 'Login exitoso', 'username': username})
        }
    except Exception as e:
        print(f"[ERROR] Error en login: {e}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
