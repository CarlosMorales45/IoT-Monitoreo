variable "region" {
  description = "Región AWS para desplegar"
  default     = "us-east-2"
}

variable "dynamodb_table_name" {
  description = "Nombre de la tabla DynamoDB para almacenar los datos de IoT"
  type        = string
  default     = "iot-monitoreo-datos"
}
