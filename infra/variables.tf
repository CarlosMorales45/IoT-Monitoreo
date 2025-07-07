variable "region" {
  description = "Región AWS para desplegar"
  default     = "us-east-2"
}

variable "dynamodb_table_name" {
  description = "Nombre de la tabla DynamoDB para almacenar los datos de IoT"
  type        = string
  default     = "iot-monitoreo-datos"
}

variable "TELEGRAM_BOT_TOKEN" {
  description = "Token del bot de Telegram para notificaciones"
  type        = string
}

variable "TELEGRAM_CHAT_ID" {
  description = "Chat ID de Telegram para enviar notificaciones"
  type        = string
}

# Variables para SQS
variable "iot_events_queue_name" {
  description = "Nombre de la cola SQS para eventos IoT"
  type        = string
  default     = "iot-events-queue"
}

variable "iot_dlq_name" {
  description = "Nombre de la Dead Letter Queue para SQS"
  type        = string
  default     = "iot-events-dlq"
}
