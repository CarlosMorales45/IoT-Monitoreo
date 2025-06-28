# Sistema de Monitoreo Inteligente de Dispositivos IoT — Infraestructura como Código (IaC)

&#x20;&#x20;

---

## ✨ Descripción

Proyecto de referencia para el **despliegue automatizado y seguro** de una plataforma de monitoreo IoT en AWS usando **Terraform** y mejores prácticas de Infraestructura como Código (IaC).\
Incluye **backend serverless, base de datos, mensajería, notificaciones, dashboard web** y **pipeline CI/CD** con validaciones de seguridad y cumplimiento normativo.

---

## 🗺️ Arquitectura

&#x20;

### **Componentes principales**

- **AWS VPC, Subnets, Security Groups**
- **API Gateway** para exponer endpoints RESTful
- **Lambda Functions** para procesamiento serverless
- **DynamoDB** para almacenamiento NoSQL de eventos
- **SQS / SNS** para mensajería y notificaciones multicanal
- **S3 + CloudFront/Cloudflare** para el dashboard web (React.js)
- **IAM Roles y Policies** seguros, sin wildcards
- **CloudWatch** para logs y métricas
- **KMS** para cifrado de recursos y variables de entorno
- **CI/CD**: GitHub Actions/Jenkins para pipeline automatizado de validación y despliegue

---

## ⚡ Despliegue rápido

1. **Clona el repositorio**

   ```bash
   git clone https://github.com/tu-usuario/iac-iot-monitoring-v2.git
   cd iac-iot-monitoring-v2/infra
   ```

2. **Configura tus credenciales de AWS**

   - Variables de entorno:
     ```bash
     export AWS_ACCESS_KEY_ID="TU_KEY"
     export AWS_SECRET_ACCESS_KEY="TU_SECRET"
     export AWS_DEFAULT_REGION="us-east-2"
     ```
   - O usa el archivo `~/.aws/credentials`.

3. **Inicializa y despliega**

   ```bash
   terraform init
   terraform validate
   terraform plan
   terraform apply -auto-approve
   ```

4. **Verifica la infraestructura creada en AWS**

---

## 🛡️ Seguridad y cumplimiento

- **Principio de privilegio mínimo**: No se usan wildcards ni permisos amplios.
- **Cifrado en todos los recursos** (DynamoDB, S3, SQS, SNS, logs).
- **Variables de entorno de Lambda cifradas con KMS**.
- **Checkov y tfsec** para análisis automático de IaC en CI/CD.
- **State backend** seguro en S3 + DynamoDB (locking).
- **CloudWatch Logs** y retención adecuada (≥ 365 días).

---

## 🤖 Pipeline CI/CD (GitHub Actions/Jenkins)

- **Validación automática:**
  - Formato (`terraform fmt`)
  - Sintaxis (`terraform validate`)
  - Seguridad (`checkov`, `tfsec`)
  - Linter y tests para Lambdas y React (opcional)
- **Despliegue automatizado a AWS**
- **Resultados y artefactos** almacenados como evidencia

```yaml
name: IaC Pipeline

on: [push, pull_request]

jobs:
  iac-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Instalar Terraform y Checkov
        run: |
          sudo apt-get update
          sudo apt-get install -y terraform
          pip install checkov
      - name: Validar Terraform
        run: |
          cd infra
          terraform fmt -check
          terraform validate
      - name: Análisis de seguridad con Checkov
        run: |
          cd infra
          checkov -d .
```

---

## 📊 Evidencia y resultados

- **Reportes de Checkov y tfsec** incluidos en `resultados/`
- **Capturas de recursos en AWS** (ver carpeta `/docs/evidencia`)
- **Logs de CI/CD** disponibles como artefactos de los workflows

---

## 📦 Estructura del repositorio

```plaintext
iac-iot-monitoring-v2/
├── infra/                  # Terraform modular
├── backend/                # Código de Lambdas
├── frontend/               # Dashboard React
├── docs/                   # Documentación y diagramas
├── resultados/             # Scans de seguridad y CI
├── .github/workflows/      # Pipeline de GitHub Actions
├── .gitignore
└── README.md
```

---

## 📝 Documentación adicional

- [Manual de despliegue paso a paso](docs/manual_despliegue.md)
- [Guía rápida para desarrolladores](docs/guia_rapida.md)
- [Buenas prácticas y checklist IaC](docs/checklist_iac.md)

---

## 📣 Autores

- **Carlos [Tu Apellido]** — Arquitectura, IaC y documentación
- [Otros colaboradores]

---

## 📄 Licencia

MIT © 2024

---

