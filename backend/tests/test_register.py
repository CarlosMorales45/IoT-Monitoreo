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

def test_register_handler_user_exists(monkeypatch):
    mod = load_lambda_module(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'lambdas', 'lambda_register_user', 'main.py')
        )
    )
    def fake_get_item(Key):
        return {'Item': {'username': 'test'}}
    mod.table.get_item = fake_get_item

    event = {"body": json.dumps({"username": "test", "password": "pass"})}
    response = mod.lambda_handler(event, None)
    assert response['statusCode'] == 409

def test_register_handler_new_user(monkeypatch):
    mod = load_lambda_module(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'lambdas', 'lambda_register_user', 'main.py')
        )
    )
    def fake_get_item(Key):
        return {}
    def fake_put_item(Item):
        return {}
    mod.table.get_item = fake_get_item
    mod.table.put_item = fake_put_item

    event = {"body": json.dumps({"username": "newuser", "password": "pass"})}
    response = mod.lambda_handler(event, None)
    assert response['statusCode'] == 201
