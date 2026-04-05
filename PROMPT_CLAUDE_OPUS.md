# Agente AllpFit — Prompt Master para Claude Opus

## 🎯 CONTEXTO DO PROJETO

Você vai construir o **Agente AllpFit**, um assistente de IA pessoal e privado que roda 100% local em um Mac, integrado com Obsidian para gestão da academia AllpFit Maceió (Brasil). O sistema transforma mensagens informais (futuramente via WhatsApp) em notas estruturadas no Obsidian, com capacidade de busca, categorização e resumos automáticos.

## 🏗️ ARQUITETURA ATUAL (base existente)

O sistema já funciona com 4 camadas:

1. **Cérebro (Ollama + Gemma4)** — Geração de respostas via `http://127.0.0.1:11434/api/generate`
2. **Ouvido (Flask)** — Servidor Python na porta 5000 com endpoint `/webhook`
3. **Mão (Parser XML)** — Extrai tags `<titulo>`, `<conteudo>` e salva arquivos .md
4. **Memória (Obsidian)** — Pasta SecCerebro em `/Users/richelcalazans/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecCerebro`

### Código atual (`agente.py`):

```python
import requests
from flask import Flask, request, jsonify
import os
import re

app = Flask(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OBSIDIAN_VAULT_PATH = "/Users/richelcalazans/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecCerebro"

def salvar_no_obsidian(titulo, conteudo):
    os.makedirs(OBSIDIAN_VAULT_PATH, exist_ok=True)
    titulo_limpo = "".join(c for c in titulo if c.isalnum() or c in " _-").strip()
    caminho_arquivo = os.path.join(OBSIDIAN_VAULT_PATH, f"{titulo_limpo}.md")
    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo.strip())
    return caminho_arquivo

def processar_texto_e_salvar(resposta_ia):
    padrao = r'<titulo>(.*?)</titulo>\s*<conteudo>(.*?)</conteudo>'
    matches = re.findall(padrao, resposta_ia, re.IGNORECASE | re.DOTALL)
    resposta_limpa = resposta_ia
    if matches:
        for titulo, conteudo in matches:
            caminho = salvar_no_obsidian(titulo, conteudo)
            print(f"\n[OBSIDIAN] ✅ ARQUIVO CRIADO: {caminho}")
            aviso = f"\n✅ *(Nota '{titulo.strip()}' organizada e salva no seu Obsidian!)*"
            resposta_limpa = re.sub(r'<nota>.*?</nota>', aviso, resposta_limpa, flags=re.IGNORECASE | re.DOTALL)
    else:
        print("\n[AVISO] A IA conversou normalmente e não criou notas.")
    return resposta_limpa

def consultar_ollama(mensagem_usuario):
    prompt_sistema = (
        "Você é o assistente pessoal do Richel na AllpFit Maceió.\n"
        "SEMPRE que o usuário pedir para 'salvar', 'anotar', ou 'criar nota', você DEVE OBRIGATORIAMENTE "
        "formatar a nota usando as seguintes tags XML:\n\n"
        "<nota>\n"
        "<titulo>Escreva o Titulo Aqui</titulo>\n"
        "<conteudo>Escreva o conteudo da nota aqui, com bullet points e detalhes.</conteudo>\n"
        "</nota>\n\n"
        "Se não for um pedido para salvar, apenas responda normalmente.\n"
        f"Mensagem do usuário: {mensagem_usuario}"
    )
    payload = {
        "model": "gemma4:e4b",
        "prompt": prompt_sistema,
        "stream": False
    }
    try:
        resposta = requests.post(OLLAMA_URL, json=payload)
        if resposta.status_code == 200:
            return processar_texto_e_salvar(resposta.json().get("response", ""))
        else:
            return f"Erro: Status {resposta.status_code}"
    except Exception as e:
        return f"Erro: {e}"

@app.route('/webhook', methods=['POST'])
def receber_whatsapp():
    dados = request.json
    mensagem_recebida = dados.get("text", "")
    remetente = dados.get("sender", "")
    print(f"\n[WHATSAPP] Mensagem recebida: {mensagem_recebida}")
    resposta_ia = consultar_ollama(mensagem_recebida)
    print(f"[IA] Resposta final:\n{resposta_ia}\n")
    return jsonify({"status": "sucesso"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
```

---

## 📋 ESCOPO: 4 FASES DE CONSTRUÇÃO

Construa cada fase como um módulo independente e autocontido. Cada fase deve ser entregue em arquivos separados, com documentação de como integrar ao todo.

---

### 🧠 FASE 1 — ROBUSTEZ DO CÉREBRO

**Objetivo:** Tornar o pipeline de IA production-ready com parser robusto, frontmatter YAML, tratamento de erros e logs estruturados.

#### Tarefas:

1. **Parser XML robusto com `lxml` ou `xml.etree.ElementTree`**
   - Substituir regex por parser XML real
   - Suportar múltiplas notas em uma única resposta
   - Suportar tags aninhadas sem quebrar
   - Fallback gracioso: se parser XML falhar, tentar regex como backup
   - Extrair metadados implícitos: detectar tags, categorias, prioridades do conteúdo

2. **Frontmatter YAML em cada nota .md**
   ```yaml
   ---
   titulo: "Reposição de Equipamentos - Março"
   data: 2025-04-05T14:30:00
   origem: "whatsapp"  # ou "terminal", "web", etc.
   remetente: "richel"
   tags: [equipamentos, reposicao, urgencia]
   categoria: "operacional"
   prioridade: "alta"
   ---
   ```
   - Gerar automaticamente a partir da resposta da IA
   - A IA deve ser instruída no prompt a classificar e taggear

3. **Tratamento de erros robusto**
   - Timeout configurável nas chamadas Ollama (máx 60s)
   - Retry automático com backoff exponencial (3 tentativas)
   - Fallback: se Ollama estiver offline, responder com mensagem útil
   - Validação de resposta: garantir que JSON da resposta Ollama é válido
   - Log de todos os erros com stack trace

4. **Sistema de logs estruturados**
   - Usar `logging` do Python com formatação JSON
   - Logs em `logs/agente_YYYY-MM-DD.log`
   - Níveis: DEBUG (parser), INFO (notas criadas), WARNING (retries), ERROR (falhas)
   - Estrutura: `{"timestamp": "...", "level": "...", "module": "...", "message": "...", "metadata": {}}`

5. **Arquivo de configuração externo (`config.yaml`)**
   ```yaml
   ollama:
     url: "http://127.0.0.1:11434/api/generate"
     model: "gemma4:e4b"
     timeout: 60
     max_retries: 3
   obsidian:
     vault_path: "/Users/richelcalazans/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecCerebro"
     subpastas:
       notas: "Notas"
       tarefas: "Tarefas"
       ideias: "Ideias"
   servidor:
     porta: 5000
     host: "127.0.0.1"
   ```

**Entregáveis da Fase 1:**
- `agente_robusto.py` (versão melhorada do agente.py)
- `config.yaml` (arquivo de configuração)
- `requirements_fase1.txt`
- `docs/fase1_robustez.md` (instruções de migração)

---

### 🔍 FASE 2 — BUSCA, RESUMOS E CATEGORIZAÇÃO

**Objetivo:** Permitir que o agente busque, resuma e organize notas existentes no vault Obsidian.

#### Tarefas:

1. **Motor de busca no vault**
   - Função `buscar_notas(query, max_resultados=5)`
   - Busca por: título, tags, conteúdo (full-text)
   - Ranking por relevância (TF-IDF simples ou similaridade de cosseno)
   - Suporte a filtros: `tags:tarefa prioridade:alta data:>2025-01-01`
   - Retornar resultados formatados com trechos relevantes

2. **Sistema de resumos automáticos**
   - Comando: "resuma as notas da semana" ou "o que tenho pendente?"
   - A IA lê notas existentes e gera síntese
   - Suporte a resumos por: dia, semana, mês, categoria
   - Salvar resumo como nova nota com link para notas originais

3. **Categorização automática**
   - Ao salvar nota, classificar automaticamente em categorias:
     - `operacional` (equipamentos, manutenção, estoque)
     - `pessoal` (alunos, treinos, avaliações)
     - `financeiro` (pagamentos, custos, receitas)
     - `marketing` (redes sociais, promoções)
     - `estrategico` (planos, metas, expansões)
   - Detectar tags automaticamente do conteúdo
   - Detectar prioridade: alta, media, baixa

4. **Comandos de consulta via mensagem**
   - `"busca sobre equipamentos"` → retorna notas relevantes
   - `"resumo da semana"` → gera resumo das últimas 7 dias
   - `"quais tarefas pendentes?"` → lista notas não marcadas como concluídas
   - `"mostra notas de janeiro"` → filtra por data

**Entregáveis da Fase 2:**
- `modulo_busca.py`
- `modulo_resumos.py`
- `modulo_categorizacao.py`
- `docs/fase2_busca_resumos.md`

---

### 📱 FASE 3 — PREPARAÇÃO PARA WHATSAPP

**Objetivo:** Estruturar o webhook para integração futura com WhatsApp (agora via curl, pronto para Evolution API ou similar).

#### Tarefas:

1. **Adapter pattern para mensageria**
   - Criar interface `MensageriaAdapter` com métodos:
     - `receber_mensagem(dados_brutos) → dict`
     - `enviar_resposta(remetente, mensagem) → bool`
   - Implementar `AdapterTerminal` (atual, via curl)
   - Implementar `AdapterWhatsAppGenerico` (pronto para Evolution API, WPPConnect, etc.)
   - Fácil trocar de adapter no `config.yaml`

2. **Webhook robusto com autenticação**
   - Endpoint `/webhook` com validação de token secreto
   - Rate limiting básico (máx 30 req/min)
   - Sanitização de input (remover caracteres maliciosos)
   - Suporte a múltiplos remetentes (preparar para grupo familiar)

3. **Formatação de resposta para WhatsApp**
   - Suporte a Markdown do WhatsApp: `*negrito*`, `_itálico_`, `~tachado~`, ```monospace```
   - Quebrar mensagens longas em partes (máx 4096 chars)
   - Enviar confirmação de recebimento: `"✅ Recebi sua mensagem: '...'"`
   - Enviar confirmação de salvamento: `"📝 Nota 'Reposição de Equipamentos' salva no Obsidian!"`

4. **Endpoint de health check**
   - `/health` → `{"status": "ok", "ollama": "connected", "obsidian": "writable", "uptime": "..."}`
   - `/stats` → `{"notas_criadas": 42, "buscas_realizadas": 15, "uptime": "..."}`

**Entregáveis da Fase 3:**
- `adapter_mensageria.py` (com adapters)
- `webhook_handler.py` (endpoint robusto)
- `docs/fase3_whatsapp.md` (guia de integração com Evolution API)

---

### 🧪 FASE 4 — TESTES E QUALIDADE

**Objetivo:** Garantir que tudo funciona com testes automatizados.

#### Tarefas:

1. **Testes unitários**
   - Testar parser XML com casos normais e edge cases
   - Testar geração de frontmatter
   - Testar categorização
   - Testar sanitização de input
   - Mock do Ollama para não depender do servidor rodando

2. **Testes de integração**
   - Testar fluxo completo: mensagem → IA → parser → Obsidian
   - Testar busca e resumo
   - Testar webhook com `requests.post`

3. **Testes do adapter WhatsApp**
   - Simular payload da Evolution API
   - Testar formatação de resposta

4. **Script de smoke test**
   - `scripts/smoke_test.sh` que:
     - Inicia o servidor
     - Envia curl de teste
     - Verifica nota criada
     - Verifica health check
     - Limpa arquivos de teste

**Entregáveis da Fase 4:**
- `tests/test_parser.py`
- `tests/test_busca.py`
- `tests/test_categorizacao.py`
- `tests/test_webhook.py`
- `tests/conftest.py` (fixtures)
- `scripts/smoke_test.sh`
- `requirements_dev.txt`

---

## 🎨 CONVENÇÕES DE CÓDIGO

- **Python 3.10+** (tipo hints em tudo)
- **Type hints** obrigatórios em todas as funções
- **Docstrings** no formato Google
- **PEP 8** com `ruff` como linter
- **Sem globals** — usar classes com injeção de dependência
- **Logging** em vez de prints
- **Config centralizada** via `config.yaml`

## 📁 ESTRUTURA FINAL ESPERADA

```
agente_allpfit/
├── agente.py                    # Ponto de entrada principal (refatorado)
├── config.yaml                  # Configurações
├── config.example.yaml          # Exemplo para copiar
├── requirements.txt             # Dependências
├── requirements_dev.txt         # Dependências de dev
├── README.md                    # Documentação principal
├── core/
│   ├── parser.py                # Parser XML robusto
│   ├── obsidian.py              # Salvamento + frontmatter
│   ├── busca.py                 # Motor de busca
│   ├── resumos.py               # Gerador de resumos
│   └── categorizacao.py         # Classificação automática
├── adapters/
│   ├── base.py                  # Interface MensageriaAdapter
│   ├── terminal.py              # Adapter para curl/terminal
│   └── whatsapp.py              # Adapter genérico (Evolution API ready)
├── api/
│   ├── webhook.py               # Flask endpoints
│   └── health.py                # Health check e stats
├── logs/                        # Logs estruturados
├── tests/
│   ├── conftest.py
│   ├── test_parser.py
│   ├── test_busca.py
│   ├── test_categorizacao.py
│   └── test_webhook.py
├── scripts/
│   ├── smoke_test.sh
│   └── start.sh                 # Script de inicialização
└── docs/
    ├── fase1_robustez.md
    ├── fase2_busca_resumos.md
    ├── fase3_whatsapp.md
    └── arquitetura.md           # Visão geral do sistema
```

## ⚙️ INSTRUÇÕES DE CONSTRUÇÃO

1. **Construa fase por fase** — cada fase deve funcionar independentemente
2. **Comece pelo `config.yaml` e estrutura de pastas** — base para todo o resto
3. **Mantenha compatibilidade retroativa** — o comando `curl` atual deve continuar funcionando
4. **Documente decisões** — explique POR QUE escolheu certa lib ou padrão
5. **Inclua exemplos de uso** — em cada doc, mostre comandos reais de teste
6. **Pense no Richel** — ele não é dev profissional; tudo deve ser simples de rodar (`./scripts/start.sh` e pronto)

## 🚀 COMANDOS QUE DEVEM FUNCIONAR NO FINAL

```bash
# Iniciar o agente
./scripts/start.sh

# Testar com curl (simulando WhatsApp)
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "Salva isso: repor 3 halteres de 10kg até segunda", "sender": "richel"}'

# Buscar notas
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "busca sobre equipamentos", "sender": "richel"}'

# Resumo semanal
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "resumo da semana", "sender": "richel"}'

# Health check
curl http://127.0.0.1:5000/health

# Rodar testes
pytest tests/ -v

# Smoke test
./scripts/smoke_test.sh
```

## 📝 NOTA FINAL

O usuário final (Richel) é personal trainer, não desenvolvedor. A experiência de uso deve ser:
- **Zero configuração** após instalar (scripts fazem tudo)
- **Feedback claro** em português (logs podem ser em inglês)
- **Resiliente** — se Ollama cair, avisar e não crashar
- **Útil** — cada interação deve gerar valor real (nota salva, busca útil, resumo acionável)

Construa com carinho. Este é o cérebro digital da academia dele. 🏋️‍♂️🧠
