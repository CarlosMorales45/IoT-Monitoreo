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

def test_list_devices(monkeypatch):
    mod = load_lambda_module(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'lambdas', 'lambda_list_devices', 'main.py')
        )
    )
    def fake_scan(FilterExpression):
        return {'Items': [
            {'device_id': 'abc123', 'nombre': 'Sensor 1', 'username': 'test'},
            {'device_id': 'def456', 'nombre': 'Sensor 2', 'username': 'test'},
        ]}
    mod.table.scan = fake_scan

    event = {"body": json.dumps({"username": "test"})}
    response = mod.lambda_handler(event, None)
    assert response['statusCode'] == 200
    items = json.loads(response['body'])
    assert isinstance(items, list)
    assert len(items) == 2
