output "dynamodb_table_name" {
  value       = aws_dynamodb_table.iot_data.name
  description = "Nombre de la tabla DynamoDB para monitoreo IoT"
}

output "api_url" {
  value       = "https://${aws_api_gateway_rest_api.iot_api.id}.execute-api.${var.region}.amazonaws.com/prod"
  description = "URL base de la API RESTful para IoT Monitoreo"
}

output "iot_events_queue_url" {
  description = "URL de la cola SQS de eventos IoT"
  value       = aws_sqs_queue.iot_events.url
}

output "iot_events_queue_arn" {
  description = "ARN de la cola SQS de eventos IoT"
  value       = aws_sqs_queue.iot_events.arn
}

output "frontend_bucket_name" {
  description = "Nombre del bucket S3 para el dashboard"
  value       = aws_s3_bucket.frontend.bucket
}
