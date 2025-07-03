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

        # Chequear si el usuario ya existe
        response = table.get_item(Key={'username': username})
        if 'Item' in response:
            return {
                'statusCode': 409,
                'body': json.dumps({'error': 'El usuario ya existe'})
            }

        # Guardar usuario
        table.put_item(Item={'username': username, 'password': password})
        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Usuario registrado', 'username': username})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
