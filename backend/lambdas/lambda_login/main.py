import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['USERS_TABLE_NAME'])

def lambda_handler(event, context):
    try:
        body = event.get('body')
        if body:
            body = json.loads(body)
        else:
            body = event
        username = body.get('username')
        password = body.get('password')

        if not username or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'username y password requeridos'})
            }

        response = table.get_item(Key={'username': username})
        user = response.get('Item')
        if not user or user.get('password') != password:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Credenciales inválidas'})
            }

        # Si es un prototipo puedes retornar sólo "ok" o los datos mínimos.
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Login exitoso', 'username': username})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
