# Como Conectar o WhatsApp

Este guia mostra como conectar seu agente ao WhatsApp usando a Evolution API.

## 1. Instalar a Evolution API

```bash
docker run -d --name evolution -p 8080:8080 atendai/evolution-api
```

## 2. Criar config.yaml

Crie um arquivo `config.yaml` na raiz do projeto:

```yaml
whatsapp:
  enabled: true
  api_url: "http://localhost:8080"
  api_key: "SUA_CHAVE_AQUI"
  instance: "allpfit"
```

## 3. Configurar Webhook na Evolution API

Configure o webhook na Evolution API para apontar para:
```
http://SEU_IP:5000/webhook
```

## 4. Iniciar o Agente

```bash
python agente.py
```

## Alternar entre Terminal e WhatsApp

O sistema usa adapters. Para alternar entre Terminal (curl) e WhatsApp:

- **WhatsApp**: mude `enabled: true` no config.yaml
- **Terminal**: mude `enabled: false` (já é o padrão)