# Fase 2 — Busca, Resumos e Categorização

## Motor de Busca

Busca full-text com ranking TF-IDF no vault Obsidian.

### Uso via mensagem

```bash
# Buscar por termo
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "busca sobre equipamentos", "sender": "richel"}'

# Buscar com filtros
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "busca categoria:financeiro pagamento", "sender": "richel"}'
```

### Filtros disponíveis

- `tags:nome` — filtra por tag
- `categoria:operacional` — filtra por categoria
- `prioridade:alta` — filtra por prioridade
- `data:>2025-01-01` — notas após uma data

## Resumos Automáticos

```bash
# Resumo da semana
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "resumo da semana", "sender": "richel"}'

# Tarefas pendentes
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "o que tenho pendente?", "sender": "richel"}'
```

Períodos: `dia`, `semana`, `quinzena`, `mes`

## Categorização Automática

Cada nota é classificada automaticamente ao ser salva:

| Categoria | Exemplos de palavras-chave |
|-----------|---------------------------|
| operacional | equipamento, manutenção, estoque, haltere |
| pessoal | aluno, treino, avaliação, ficha |
| financeiro | pagamento, mensalidade, custo, pix |
| marketing | instagram, post, promoção, campanha |
| estrategico | meta, plano, expansão, projeto |

Prioridade: `alta` (urgente, hoje, quebrou), `media` (padrão), `baixa` (quando puder)
