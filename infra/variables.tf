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