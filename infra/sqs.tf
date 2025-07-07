# ========== Dead Letter Queue para SQS ==========
resource "aws_sqs_queue" "iot_events_dlq" {
  name                       = var.iot_dlq_name
  message_retention_seconds   = 1209600 # 14 días
}

# ========== SQS QUEUE PARA EVENTOS IoT ==========
resource "aws_sqs_queue" "iot_events" {
  name                        = var.iot_events_queue_name
  visibility_timeout_seconds  = 30
  message_retention_seconds   = 86400 # 1 día

  # Política DLQ: Si un mensaje falla 5 veces, va a la DLQ
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.iot_events_dlq.arn
    maxReceiveCount     = 5
  })
}

# ========== PERMISOS IAM para que las Lambdas puedan enviar/recibir mensajes ==========
resource "aws_iam_role_policy" "lambda_sqs_policy" {
  name = "lambda-sqs-policy"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ],
        Resource = aws_sqs_queue.iot_events.arn
      },
      {
        Effect = "Allow",
        Action = [
          "sqs:SendMessage"
        ],
        Resource = aws_sqs_queue.iot_events_dlq.arn
      }
    ]
  })
}