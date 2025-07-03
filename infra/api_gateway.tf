resource "aws_api_gateway_rest_api" "iot_api" {
  name        = "iot-monitoreo-api"
  description = "API RESTful para IoT Monitoreo"
}

# RESOURCE: /devices
resource "aws_api_gateway_resource" "devices" {
  rest_api_id = aws_api_gateway_rest_api.iot_api.id
  parent_id   = aws_api_gateway_rest_api.iot_api.root_resource_id
  path_part   = "devices"
}

# RESOURCE: /devices/{device_id}
resource "aws_api_gateway_resource" "device_id" {
  rest_api_id = aws_api_gateway_rest_api.iot_api.id
  parent_id   = aws_api_gateway_resource.devices.id
  path_part   = "{device_id}"
}

### Métodos REST para /devices

# POST /devices
resource "aws_api_gateway_method" "post_device" {
  rest_api_id   = aws_api_gateway_rest_api.iot_api.id
  resource_id   = aws_api_gateway_resource.devices.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "post_device_integration" {
  rest_api_id             = aws_api_gateway_rest_api.iot_api.id
  resource_id             = aws_api_gateway_resource.devices.id
  http_method             = aws_api_gateway_method.post_device.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.register_device.invoke_arn
}
# GET /devices
resource "aws_api_gateway_method" "get_devices" {
  rest_api_id   = aws_api_gateway_rest_api.iot_api.id
  resource_id   = aws_api_gateway_resource.devices.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "get_devices_integration" {
  rest_api_id             = aws_api_gateway_rest_api.iot_api.id
  resource_id             = aws_api_gateway_resource.devices.id
  http_method             = aws_api_gateway_method.get_devices.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.list_devices.invoke_arn
}

# OPTIONS /devices (para CORS)
resource "aws_api_gateway_method" "options_devices" {
  rest_api_id   = aws_api_gateway_rest_api.iot_api.id
  resource_id   = aws_api_gateway_resource.devices.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "options_devices_integration" {
  rest_api_id             = aws_api_gateway_rest_api.iot_api.id
  resource_id             = aws_api_gateway_resource.devices.id
  http_method             = aws_api_gateway_method.options_devices.http_method
  type                    = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
  integration_http_method = "OPTIONS"
}
resource "aws_api_gateway_method_response" "options_devices_200" {
  rest_api_id = aws_api_gateway_rest_api.iot_api.id
  resource_id = aws_api_gateway_resource.devices.id
  http_method = aws_api_gateway_method.options_devices.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
  response_models = { "application/json" = "Empty" }
}
resource "aws_api_gateway_integration_response" "options_devices_200" {
  rest_api_id = aws_api_gateway_rest_api.iot_api.id
  resource_id = aws_api_gateway_resource.devices.id
  http_method = aws_api_gateway_method.options_devices.http_method
  status_code = aws_api_gateway_method_response.options_devices_200.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
  }
}

# --- Métodos REST para /devices/{device_id} ---
# GET
resource "aws_api_gateway_method" "get_device" {
  rest_api_id   = aws_api_gateway_rest_api.iot_api.id
  resource_id   = aws_api_gateway_resource.device_id.id
  http_method   = "GET"
  authorization = "NONE"
  request_parameters = {
    "method.request.path.device_id" = true
  }
}
resource "aws_api_gateway_integration" "get_device_integration" {
  rest_api_id             = aws_api_gateway_rest_api.iot_api.id
  resource_id             = aws_api_gateway_resource.device_id.id
  http_method             = aws_api_gateway_method.get_device.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_device.invoke_arn
  request_parameters = {
    "integration.request.path.device_id" = "method.request.path.device_id"
  }
}
# PUT
resource "aws_api_gateway_method" "put_device" {
  rest_api_id   = aws_api_gateway_rest_api.iot_api.id
  resource_id   = aws_api_gateway_resource.device_id.id
  http_method   = "PUT"
  authorization = "NONE"
  request_parameters = {
    "method.request.path.device_id" = true
  }
}
resource "aws_api_gateway_integration" "put_device_integration" {
  rest_api_id             = aws_api_gateway_rest_api.iot_api.id
  resource_id             = aws_api_gateway_resource.device_id.id
  http_method             = aws_api_gateway_method.put_device.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.update_device.invoke_arn
  request_parameters = {
    "integration.request.path.device_id" = "method.request.path.device_id"
  }
}
# DELETE
resource "aws_api_gateway_method" "delete_device" {
  rest_api_id   = aws_api_gateway_rest_api.iot_api.id
  resource_id   = aws_api_gateway_resource.device_id.id
  http_method   = "DELETE"
  authorization = "NONE"
  request_parameters = {
    "method.request.path.device_id" = true
  }
}
resource "aws_api_gateway_integration" "delete_device_integration" {
  rest_api_id             = aws_api_gateway_rest_api.iot_api.id
  resource_id             = aws_api_gateway_resource.device_id.id
  http_method             = aws_api_gateway_method.delete_device.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.delete_device.invoke_arn
  request_parameters = {
    "integration.request.path.device_id" = "method.request.path.device_id"
  }
}
# OPTIONS /devices/{device_id} (CORS)
resource "aws_api_gateway_method" "options_device_id" {
  rest_api_id   = aws_api_gateway_rest_api.iot_api.id
  resource_id   = aws_api_gateway_resource.device_id.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "options_device_id_integration" {
  rest_api_id             = aws_api_gateway_rest_api.iot_api.id
  resource_id             = aws_api_gateway_resource.device_id.id
  http_method             = aws_api_gateway_method.options_device_id.http_method
  type                    = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
  integration_http_method = "OPTIONS"
}
resource "aws_api_gateway_method_response" "options_device_id_200" {
  rest_api_id = aws_api_gateway_rest_api.iot_api.id
  resource_id = aws_api_gateway_resource.device_id.id
  http_method = aws_api_gateway_method.options_device_id.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
  response_models = { "application/json" = "Empty" }
}
resource "aws_api_gateway_integration_response" "options_device_id_200" {
  rest_api_id = aws_api_gateway_rest_api.iot_api.id
  resource_id = aws_api_gateway_resource.device_id.id
  http_method = aws_api_gateway_method.options_device_id.http_method
  status_code = aws_api_gateway_method_response.options_device_id_200.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
  }
}

# --- RECURSO PARA LOGIN ---
resource "aws_api_gateway_resource" "login" {
  rest_api_id = aws_api_gateway_rest_api.iot_api.id
  parent_id   = aws_api_gateway_rest_api.iot_api.root_resource_id
  path_part   = "login"
}
resource "aws_api_gateway_method" "post_login" {
  rest_api_id   = aws_api_gateway_rest_api.iot_api.id
  resource_id   = aws_api_gateway_resource.login.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "post_login_integration" {
  rest_api_id             = aws_api_gateway_rest_api.iot_api.id
  resource_id             = aws_api_gateway_resource.login.id
  http_method             = aws_api_gateway_method.post_login.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.login_user.invoke_arn
}
# OPTIONS /login
resource "aws_api_gateway_method" "options_login" {
  rest_api_id   = aws_api_gateway_rest_api.iot_api.id
  resource_id   = aws_api_gateway_resource.login.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "options_login_integration" {
  rest_api_id             = aws_api_gateway_rest_api.iot_api.id
  resource_id             = aws_api_gateway_resource.login.id
  http_method             = aws_api_gateway_method.options_login.http_method
  type                    = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
  integration_http_method = "OPTIONS"
}
resource "aws_api_gateway_method_response" "options_login_200" {
  rest_api_id = aws_api_gateway_rest_api.iot_api.id
  resource_id = aws_api_gateway_resource.login.id
  http_method = aws_api_gateway_method.options_login.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
  response_models = { "application/json" = "Empty" }
}
resource "aws_api_gateway_integration_response" "options_login_200" {
  rest_api_id = aws_api_gateway_rest_api.iot_api.id
  resource_id = aws_api_gateway_resource.login.id
  http_method = aws_api_gateway_method.options_login.http_method
  status_code = aws_api_gateway_method_response.options_login_200.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
  }
}

# --- RECURSO PARA REGISTER ---
resource "aws_api_gateway_resource" "register" {
  rest_api_id = aws_api_gateway_rest_api.iot_api.id
  parent_id   = aws_api_gateway_rest_api.iot_api.root_resource_id
  path_part   = "register"
}
resource "aws_api_gateway_method" "post_register" {
  rest_api_id   = aws_api_gateway_rest_api.iot_api.id
  resource_id   = aws_api_gateway_resource.register.id
  http_method   = "POST"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "post_register_integration" {
  rest_api_id             = aws_api_gateway_rest_api.iot_api.id
  resource_id             = aws_api_gateway_resource.register.id
  http_method             = aws_api_gateway_method.post_register.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.register_user.invoke_arn
}
# OPTIONS /register
resource "aws_api_gateway_method" "options_register" {
  rest_api_id   = aws_api_gateway_rest_api.iot_api.id
  resource_id   = aws_api_gateway_resource.register.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "options_register_integration" {
  rest_api_id             = aws_api_gateway_rest_api.iot_api.id
  resource_id             = aws_api_gateway_resource.register.id
  http_method             = aws_api_gateway_method.options_register.http_method
  type                    = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
  integration_http_method = "OPTIONS"
}
resource "aws_api_gateway_method_response" "options_register_200" {
  rest_api_id = aws_api_gateway_rest_api.iot_api.id
  resource_id = aws_api_gateway_resource.register.id
  http_method = aws_api_gateway_method.options_register.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
  response_models = { "application/json" = "Empty" }
}
resource "aws_api_gateway_integration_response" "options_register_200" {
  rest_api_id = aws_api_gateway_rest_api.iot_api.id
  resource_id = aws_api_gateway_resource.register.id
  http_method = aws_api_gateway_method.options_register.http_method
  status_code = aws_api_gateway_method_response.options_register_200.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'*'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
  }
}

### PERMISOS PARA TODAS LAS LAMBDAS ###
resource "aws_lambda_permission" "api_gateway_invoke" {
  for_each = {
    register_device = aws_lambda_function.register_device.arn
    list_devices    = aws_lambda_function.list_devices.arn
    get_device      = aws_lambda_function.get_device.arn
    update_device   = aws_lambda_function.update_device.arn
    delete_device   = aws_lambda_function.delete_device.arn
  }
  statement_id  = "${each.key}_apigw"
  action        = "lambda:InvokeFunction"
  function_name = each.value
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.iot_api.execution_arn}/*/*"
}
resource "aws_lambda_permission" "login_user_apigw" {
  statement_id  = "login_user_apigw"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.login_user.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.iot_api.execution_arn}/*/*"
}
resource "aws_lambda_permission" "register_user_apigw" {
  statement_id  = "register_user_apigw"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.register_user.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.iot_api.execution_arn}/*/*"
}

# DEPLOYMENT y STAGE
resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [
    aws_api_gateway_integration.post_device_integration,
    aws_api_gateway_integration.get_devices_integration,
    aws_api_gateway_integration.get_device_integration,
    aws_api_gateway_integration.put_device_integration,
    aws_api_gateway_integration.delete_device_integration,
    aws_api_gateway_integration.post_register_integration,
    aws_api_gateway_integration.post_login_integration,
    aws_api_gateway_integration.options_devices_integration,
    aws_api_gateway_integration.options_device_id_integration,
    aws_api_gateway_integration.options_login_integration,
    aws_api_gateway_integration.options_register_integration
  ]
  rest_api_id = aws_api_gateway_rest_api.iot_api.id
}
resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.iot_api.id
  stage_name    = "prod"
}
