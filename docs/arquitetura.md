# Arquitetura do Agente AllpFit

## Visão Geral

```
Usuário (curl/WhatsApp)
    │
    ▼
┌─────────────┐
│  Webhook     │  api/webhook.py — recebe mensagens, detecta comandos
│  (Flask)     │
└──────┬──────┘
       │
       ├── Comando de busca? ──▶ core/busca.py ──▶ Resposta
       ├── Comando de resumo? ─▶ core/resumos.py ──▶ Resposta
       │
       ▼
┌─────────────┐
│  Ollama      │  core/ollama.py — envia prompt, recebe resposta
│  (Gemma4)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Parser      │  core/parser.py — extrai notas da resposta XML
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Categorizar  │  core/categorizacao.py — classifica categoria/prioridade/tags
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Obsidian    │  core/obsidian.py — salva .md com frontmatter YAML
│  (Vault)     │
└─────────────┘
```

## Módulos

| Módulo | Arquivo | Descrição |
|--------|---------|-----------|
| Config | `core/config.py` | Carrega config.yaml em dataclasses |
| Logger | `core/logger.py` | Logs JSON em arquivo + console |
| Parser | `core/parser.py` | Extrai notas XML da resposta IA |
| Obsidian | `core/obsidian.py` | Salva notas com frontmatter |
| Ollama | `core/ollama.py` | Cliente IA com retry |
| Busca | `core/busca.py` | Busca TF-IDF no vault |
| Resumos | `core/resumos.py` | Gera resumos por período |
| Categorização | `core/categorizacao.py` | Classifica notas |
| Adapter Terminal | `adapters/terminal.py` | Recebe/responde via curl |
| Adapter WhatsApp | `adapters/whatsapp.py` | Pronto para Evolution API |
| Webhook | `api/webhook.py` | Endpoints Flask |
| Health | `api/health.py` | Health check e stats |

## Como Rodar

```bash
./scripts/start.sh
```

Isso cria o venv, instala dependências, verifica Ollama e inicia o servidor.

## Como Testar

```bash
# Testes automatizados
pip install -r requirements_dev.txt
pytest tests/ -v

# Smoke test (precisa do servidor rodando)
./scripts/smoke_test.sh
```
