# Fase 3 — Preparação para WhatsApp

## Arquitetura de Adapters

O sistema usa o padrão Adapter para abstrair o canal de comunicação:

```
MensageriaAdapter (interface)
├── AdapterTerminal   — para uso via curl (atual)
└── AdapterWhatsApp   — para Evolution API / WPPConnect
```

## Uso Atual (Terminal)

Nada muda. Continue usando curl normalmente:

```bash
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "sua mensagem", "sender": "richel"}'
```

## Integração com WhatsApp (Evolution API)

Quando estiver pronto para integrar com WhatsApp:

### 1. Instale a Evolution API

```bash
docker run -d --name evolution \
  -p 8080:8080 \
  atendai/evolution-api
```

### 2. Configure o webhook na Evolution API

Aponte o webhook da instância para:
```
http://SEU_IP:5000/webhook
```

### 3. O adapter já entende o payload da Evolution API

Formato recebido:
```json
{
  "data": {
    "key": {"remoteJid": "5582999999999@s.whatsapp.net"},
    "message": {"conversation": "Salva isso: repor halteres"}
  }
}
```

## Health Check

```bash
# Status geral
curl http://127.0.0.1:5000/health
# {"status": "ok", "ollama": "connected", "obsidian": "writable", "uptime": "1h 23m 45s"}

# Estatísticas
curl http://127.0.0.1:5000/stats
# {"notas_criadas": 42, "buscas_realizadas": 15, "resumos_gerados": 3, "erros": 0}
```

## Segurança

- **Rate limiting**: máx 30 requisições/minuto por IP
- **Token de autenticação** (opcional): envie no header `X-Auth-Token`
- **Sanitização de input**: caracteres de controle são removidos, mensagens limitadas a 2000 chars
