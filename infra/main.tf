provider "aws" {
  region = var.region
}

# --- 1. Red principal VPC ---
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags       = { Name = "iot-vpc" }
}

# --- 2. Subnet pública ---
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-2a"
  map_public_ip_on_launch = true
  tags                    = { Name = "iot-subnet-public" }
}

# --- 3. Security Group (solo salida) ---
resource "aws_security_group" "main_sg" {
  vpc_id = aws_vpc.main.id
  name   = "iot-sg"
  description = "Security group base para IoT"
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "iot-base-sg" }
}

# --- 4. Internet Gateway ---
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "iot-igw" }
}

# --- 5. Route Table pública ---
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "iot-public-rt" }
}

resource "aws_route" "internet_access" {
  route_table_id         = aws_route_table.public_rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.gw.id
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public_rt.id
}

# --- 6. Bucket S3 para el frontend (dashboard) ---
resource "random_id" "sufijo" {
  byte_length = 4
}

resource "aws_s3_bucket" "frontend" {
  bucket = "iot-monitoreo-dashboard-${random_id.sufijo.hex}"
  tags   = { Name = "iot-dashboard-bucket" }
}

resource "aws_s3_bucket_website_configuration" "frontend_website" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}

# --- 7. IAM Role para Lambda ---
resource "aws_iam_role" "lambda_role" {
  name = "iot-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_policy_attachment" "lambda_basic_execution" {
  name       = "lambda-basic"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# --- DynamoDB para almacenar datos de IoT ---
resource "aws_dynamodb_table" "iot_data" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "device_id"
  range_key    = "timestamp"

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"  # Permite ver cambios antes/después

  attribute {
    name = "device_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  tags = {
    Name     = var.dynamodb_table_name
    Proyecto = "IAC-Monitoreo"
  }
}

# --- Lambda: register_device ---
resource "aws_lambda_function" "register_device" {
  function_name = "register_device"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  filename         = "${path.module}/../backend/lambda_build/lambda_register_device.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/lambda_build/lambda_register_device.zip")

  role = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
    }
  }

  timeout = 10
}

# --- Lambda: get_device ---
resource "aws_lambda_function" "get_device" {
  function_name = "get_device"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  filename         = "${path.module}/../backend/lambda_build/lambda_get_device.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/lambda_build/lambda_get_device.zip")

  role = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
    }
  }

  timeout = 10
}

# --- Lambda: list_devices ---
resource "aws_lambda_function" "list_devices" {
  function_name = "list_devices"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  filename         = "${path.module}/../backend/lambda_build/lambda_list_devices.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/lambda_build/lambda_list_devices.zip")

  role = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
    }
  }

  timeout = 10
}

# --- Permisos adicionales para Lambda sobre DynamoDB ---
resource "aws_iam_role_policy" "lambda_dynamodb_policy" {
  name = "lambda-dynamodb-policy"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:DeleteItem",
          # AGREGADOS PARA STREAMS:
          "dynamodb:DescribeStream",
          "dynamodb:GetRecords",
          "dynamodb:GetShardIterator",
          "dynamodb:ListStreams"
        ],
        Resource = aws_dynamodb_table.iot_data.arn
      },
      # Permitir también acceso a los streams asociados (importante)
      {
        Effect   = "Allow",
        Action   = [
          "dynamodb:DescribeStream",
          "dynamodb:GetRecords",
          "dynamodb:GetShardIterator",
          "dynamodb:ListStreams"
        ],
        Resource = "${aws_dynamodb_table.iot_data.stream_arn}"
      }
    ]
  })
}

# --- Lambda: update_device ---
resource "aws_lambda_function" "update_device" {
  function_name = "update_device"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  filename         = "${path.module}/../backend/lambda_build/lambda_update_device.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/lambda_build/lambda_update_device.zip")

  role = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
    }
  }

  timeout = 10
}

# --- Lambda: delete_device ---
resource "aws_lambda_function" "delete_device" {
  function_name = "delete_device"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  filename         = "${path.module}/../backend/lambda_build/lambda_delete_device.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/lambda_build/lambda_delete_device.zip")

  role = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
    }
  }

  timeout = 10
}

# --- Lambda: notify_error ---
resource "aws_lambda_function" "notify_error" {
  function_name = "notify_error"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  filename         = "${path.module}/../backend/lambda_build/lambda_notify_error.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/lambda_build/lambda_notify_error.zip")

  role = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      TELEGRAM_BOT_TOKEN   = var.TELEGRAM_BOT_TOKEN
      TELEGRAM_CHAT_ID     = var.TELEGRAM_CHAT_ID
      DYNAMODB_TABLE_NAME  = var.dynamodb_table_name
    }
  }

  timeout = 10
}

# --- Lambda: notify_recovery ---
resource "aws_lambda_function" "notify_recovery" {
  function_name = "notify_recovery"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  filename         = "${path.module}/../backend/lambda_build/lambda_notify_recovery.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/lambda_build/lambda_notify_recovery.zip")

  role = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      TELEGRAM_BOT_TOKEN   = var.TELEGRAM_BOT_TOKEN
      TELEGRAM_CHAT_ID     = var.TELEGRAM_CHAT_ID
      DYNAMODB_TABLE_NAME  = var.dynamodb_table_name
    }
  }

  timeout = 10
}

# --- Trigger DynamoDB Stream para Lambda notify_error ---
resource "aws_lambda_event_source_mapping" "trigger_notify_error" {
  event_source_arn  = aws_dynamodb_table.iot_data.stream_arn
  function_name     = aws_lambda_function.notify_error.arn
  starting_position = "LATEST"
  batch_size        = 1
  enabled           = true
}

# --- Trigger DynamoDB Stream para Lambda notify_recovery ---
resource "aws_lambda_event_source_mapping" "trigger_notify_recovery" {
  event_source_arn  = aws_dynamodb_table.iot_data.stream_arn
  function_name     = aws_lambda_function.notify_recovery.arn
  starting_position = "LATEST"
  batch_size        = 1
  enabled           = true
}

# --- DynamoDB para usuarios de IoT ---
resource "aws_dynamodb_table" "iot_users" {
  name         = "iot-usuarios"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "username"
  attribute {
    name = "username"
    type = "S"
  }
  tags = {
    Name     = "iot-usuarios"
    Proyecto = "IAC-Monitoreo"
  }
}

# --- Lambda: login_user ---
resource "aws_lambda_function" "login_user" {
  function_name = "login_user"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"
  filename         = "${path.module}/../backend/lambda_build/lambda_login_user.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/lambda_build/lambda_login_user.zip")
  role = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      USERS_TABLE_NAME = aws_dynamodb_table.iot_users.name
    }
  }
  timeout = 10
}

# --- Lambda: register_user ---
resource "aws_lambda_function" "register_user" {
  function_name = "register_user"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"
  filename         = "${path.module}/../backend/lambda_build/lambda_register_user.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/lambda_build/lambda_register_user.zip")
  role = aws_iam_role.lambda_role.arn

  environment {
    variables = {
      USERS_TABLE_NAME = aws_dynamodb_table.iot_users.name
    }
  }
  timeout = 10
}

# Permisos para que la Lambda pueda escribir y leer usuarios
resource "aws_iam_role_policy" "lambda_register_user_policy" {
  name = "lambda-register-user-policy"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "dynamodb:PutItem",
          "dynamodb:GetItem"
        ],
        Resource = aws_dynamodb_table.iot_users.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_users_policy" {
  name = "lambda-users-policy"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "dynamodb:GetItem",
          "dynamodb:PutItem"
        ],
        Resource = aws_dynamodb_table.iot_users.arn
      }
    ]
  })
}
