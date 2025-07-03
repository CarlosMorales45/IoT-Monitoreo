import os
import sys
import importlib.util
import json

os.environ['DYNAMODB_TABLE_NAME'] = 'dummy-table'

def load_lambda_module(path):
    spec = importlib.util.spec_from_file_location("lambda_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_register_device_success(monkeypatch):
    mod = load_lambda_module(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'lambdas', 'lambda_register_device', 'main.py')
        )
    )
    def fake_put_item(Item):
        return {}
    mod.table.put_item = fake_put_item

    event = {"body": json.dumps({
        "device_id": "abc123",
        "nombre": "Sensor 1",
        "tipo": "temp",
        "ubicacion": "Lab",
        "estado": "activo",
        "username": "test"
    })}
    response = mod.lambda_handler(event, None)
    assert response['statusCode'] == 200

def test_register_device_missing_field():
    mod = load_lambda_module(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'lambdas', 'lambda_register_device', 'main.py')
        )
    )
    event = {"body": json.dumps({
        "nombre": "Sensor 1",
        "tipo": "temp",
        "ubicacion": "Lab",
        "estado": "activo"
    })}
    response = mod.lambda_handler(event, None)
    assert response['statusCode'] == 400
