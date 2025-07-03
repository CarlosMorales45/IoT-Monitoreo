import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    device_id = path_params.get("device_id")
    username = None

    try:
        body = json.loads(event.get("body") or "{}")
        username = body.get("username")
    except Exception:
        body = {}
        username = None

    timestamp = body.get("timestamp")
    update_fields = body.get("update_fields", {})

    if not device_id or not timestamp or not update_fields or not username:
        return {'statusCode': 400, 'body': json.dumps({'error': 'device_id, timestamp, update_fields y username son requeridos'})}

    # Primero verifica que el dispositivo sea del usuario
    resp = table.get_item(Key={'device_id': device_id, 'timestamp': timestamp})
    item = resp.get('Item')
    if not item or item.get('username') != username:
        return {'statusCode': 404, 'body': json.dumps({'error': 'No autorizado o dispositivo no encontrado'})}

    # Actualiza
    update_expr = []
    expr_attr_values = {}
    expr_attr_names = {}
    for k, v in update_fields.items():
        update_expr.append(f"#{k} = :{k}")
        expr_attr_values[f":{k}"] = v
        expr_attr_names[f"#{k}"] = k

    try:
        response = table.update_item(
            Key={'device_id': device_id, 'timestamp': timestamp},
            UpdateExpression="SET " + ", ".join(update_expr),
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            ReturnValues="ALL_NEW"
        )
        return {'statusCode': 200, 'body': json.dumps(response.get('Attributes', {}))}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
