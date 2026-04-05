# Fase 1 — Robustez do Cérebro

## O que mudou

O `agente.py` original foi refatorado em módulos independentes:

| Módulo | Arquivo | Responsabilidade |
|--------|---------|-----------------|
| Config | `core/config.py` | Carrega `config.yaml` em dataclasses tipadas |
| Logger | `core/logger.py` | Logs estruturados em JSON + console |
| Parser | `core/parser.py` | Parser XML real com fallback regex |
| Obsidian | `core/obsidian.py` | Salva notas com frontmatter YAML |
| Ollama | `core/ollama.py` | Cliente com retry + backoff exponencial |

## Migração do agente.py antigo

1. Copie seu `config.yaml` (já criado com seus caminhos)
2. Instale dependências: `pip install -r requirements.txt`
3. Inicie com: `python agente.py` ou `./scripts/start.sh`

O endpoint `/webhook` continua igual — seus curls antigos vão funcionar sem mudança.

## Parser XML

- Usa `xml.etree.ElementTree` ao invés de regex
- Suporta múltiplas `<nota>` em uma resposta
- Se o XML estiver malformado, faz fallback para regex automaticamente

## Frontmatter YAML

Cada nota salva agora inclui metadados:

```yaml
---
titulo: "Reposição de Equipamentos"
data: 2025-04-05T14:30:00
origem: "terminal"
remetente: "richel"
tags: ["equipamento", "reposicao"]
categoria: "operacional"
prioridade: "alta"
---
```

## Tratamento de Erros

- Timeout configurável (padrão: 60s)
- 3 tentativas com backoff exponencial (2s, 4s, 8s)
- Se Ollama estiver offline, retorna mensagem amigável (não crasha)

## Logs

Logs são salvos em `logs/agente_YYYY-MM-DD.log` em formato JSON:

```json
{"timestamp": "2025-04-05T14:30:00Z", "level": "INFO", "module": "obsidian", "message": "Nota salva: /caminho/nota.md"}
```

## Testando

```bash
# Inicia o servidor
python agente.py

# Envia uma nota
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "Salva isso: repor 3 halteres de 10kg até segunda", "sender": "richel"}'

# Verifica saúde
curl http://127.0.0.1:5000/health
```
