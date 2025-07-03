import os
import sys
import importlib.util
import json

os.environ['USERS_TABLE_NAME'] = 'dummy-users'

def load_lambda_module(path):
    spec = importlib.util.spec_from_file_location("lambda_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_login_handler_success(monkeypatch):
    mod = load_lambda_module(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'lambdas', 'lambda_login', 'main.py')
        )
    )
    def fake_get_item(Key):
        return {'Item': {'username': 'test', 'password': 'pass'}}
    mod.table.get_item = fake_get_item

    event = {"body": json.dumps({"username": "test", "password": "pass"})}
    response = mod.lambda_handler(event, None)
    assert response['statusCode'] == 200

def test_login_handler_wrong_password(monkeypatch):
    mod = load_lambda_module(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'lambdas', 'lambda_login', 'main.py')
        )
    )
    def fake_get_item(Key):
        return {'Item': {'username': 'test', 'password': 'pass'}}
    mod.table.get_item = fake_get_item

    event = {"body": json.dumps({"username": "test", "password": "fail"})}
    response = mod.lambda_handler(event, None)
    assert response['statusCode'] == 401
