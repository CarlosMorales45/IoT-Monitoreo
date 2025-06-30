import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def lambda_handler(event, context):
    device_id = event.get('device_id')
    timestamp = event.get('timestamp')
    update_fields = event.get('update_fields', {})

    if not device_id or not timestamp or not update_fields:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'device_id, timestamp y update_fields son requeridos'})
        }

    # Construir expresión de actualización
    update_expr = []
    expr_attr_values = {}
    expr_attr_names = {}
    for k, v in update_fields.items():
        update_expr.append(f"#{k} = :{k}")
        expr_attr_values[f":{k}"] = v
        expr_attr_names[f"#{k}"] = k

    try:
        response = table.update_item(
            Key={
                'device_id': device_id,
                'timestamp': timestamp
            },
            UpdateExpression="SET " + ", ".join(update_expr),
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            ReturnValues="ALL_NEW"
        )
        return {
            'statusCode': 200,
            'body': json.dumps(response.get('Attributes', {}))
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }