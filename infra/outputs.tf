output "dynamodb_table_name" {
  value       = aws_dynamodb_table.iot_data.name
  description = "Nombre de la tabla DynamoDB para monitoreo IoT"
}
