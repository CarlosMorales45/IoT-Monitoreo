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

resource "aws_s3_bucket_acl" "frontend_acl" {
  bucket = aws_s3_bucket.frontend.id
  acl    = "public-read"
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
