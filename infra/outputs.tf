output "dynamodb_table_name" {
  value       = aws_dynamodb_table.iot_data.name
  description = "Nombre de la tabla DynamoDB para monitoreo IoT"
}

output "api_url" {
  value       = "https://${aws_api_gateway_rest_api.iot_api.id}.execute-api.${var.region}.amazonaws.com/prod"
  description = "URL base de la API RESTful para IoT Monitoreo"
}
