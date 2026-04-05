# 🏋️ GUIA DE INÍCIO - AGENTE ALLPFIT
## Para Richel - Personal Trainer da Academia AllpFit

---

## 📋 SUMÁRIO RÁPIDO
1. **Verificar seu ambiente** (5 min)
2. **Ligar o projeto** (2 min)
3. **Entender a estrutura** (10 min)
4. **Testar as funcionalidades** (15 min)
5. **Ler os logs** (5 min)
6. **Resolver problemas** (referência)

---

## PARTE 1: VERIFICAR SEU AMBIENTE ✅

Seu Mac já tem tudo o que precisa:

| Item | Status | O que é |
|------|--------|---------|
| **Python 3.10** | ✅ Instalado | Linguagem de programação que executa o projeto |
| **pip** | ✅ Instalado | Gerenciador de bibliotecas Python |
| **Ollama** | ⏳ Precisa ligar | Inteligência artificial que roda offline |
| **Obsidian** | ✅ Pronto | App de notas onde o agente salva tudo |

### 🚀 Ligar o Ollama pela PRIMEIRA VEZ

1. Abra o **Terminal** no seu Mac (ou use o Spotlight: `Cmd + Espaço` e digite "Terminal")

2. Cole este comando e pressione Enter:
```bash
ollama serve
```

3. **O que você vai ver:**
```
pulling digest...
success
2025/04/05 10:30:45 listener loop starting
```

4. **Deixe rodando!** Não feche este terminal. Ele fica ouvindo na porta 11434.

**Importante:** Você precisa fazer isso ANTES de ligar o Agente AllpFit. Pode deixar em aberto enquanto trabalha.

---

## PARTE 2: LIGAR O PROJETO 🔌

Abra um **NOVO TERMINAL** (não feche o Ollama) e siga:

### Passo 1: Ir até a pasta do projeto
```bash
cd /Users/richelcalazans/agente_allpfit/agente_allpfit
```

### Passo 2: Ligar tudo
```bash
bash scripts/start.sh
```

### 🎯 O QUE VOCÊ DEVE VER:
```
==================================================
  AGENTE ALLPFIT - Iniciando...
==================================================
[SETUP] Criando ambiente virtual...
[SETUP] Verificando dependências...
[CHECK] Verificando Ollama...
[OK] Ollama está rodando
[START] Iniciando servidor na porta 5000...
        Envie mensagens com:
        curl -X POST http://127.0.0.1:5000/webhook \
          -H "Content-Type: application/json" \
          -d '{"text": "sua mensagem aqui", "sender": "richel"}'

 * Running on http://127.0.0.1:5000
```

**Se vir isso, você conseguiu!** ✅

Se vir erros, veja a seção "Resolver Problemas" no final.

---

## PARTE 3: ENTENDER A ESTRUTURA 📁

Seu projeto está organizado em pastas. Vou explicar o que cada uma faz:

### **📍 Pasta raiz: `/agente_allpfit/`**

```
agente_allpfit/
├── agente.py                 ← Arquivo principal (não mexer)
├── config.yaml              ← Suas configurações (IA, Obsidian, porta)
├── requirements.txt         ← Lista de bibliotecas que precisa
├── venv/                    ← Ambiente isolado do Python (criado automaticamente)
│
├── scripts/
│   └── start.sh            ← O script que você vai rodar
│
├── api/                     ← Parte web (recebe mensagens)
│   ├── webhook.py          ← Recebe mensagens via curl/WhatsApp
│   └── health.py           ← Verifica se está tudo ok
│
├── core/                    ← Cérebro do agente (lógica principal)
│   ├── ollama.py          ← Fala com a IA Ollama
│   ├── obsidian.py        ← Salva e busca notas no Obsidian
│   ├── parser.py          ← Analisa o que você digitou
│   ├── busca.py           ← Procura notas antigas
│   ├── categorizacao.py   ← Organiza em categorias
│   ├── resumos.py         ← Faz resumos automáticos
│   ├── config.py          ← Lê configurações
│   └── logger.py          ← Registra tudo que acontece
│
├── adapters/                ← Adaptadores (Terminal, WhatsApp, etc)
├── tests/                   ← Testes automáticos
├── logs/                    ← 📝 Arquivo de logs (você vai ver aqui)
└── docs/                    ← Documentação extra
```

### **O que cada pasta faz (em português simples):**

| Pasta | O que faz | Quando precisa mexer |
|-------|----------|---------------------|
| `core/` | Contém a lógica toda (salva, busca, entende mensagens) | Nunca (deixa quieto) |
| `api/` | Recebe mensagens do mundo externo | Nunca (deixa quieto) |
| `scripts/` | Scripts para iniciar tudo | Quando quer ligar o agente |
| `logs/` | Registra tudo que acontece | Quando quer entender erros |
| `venv/` | Cópia isolada do Python | Deixa quieto, criado automaticamente |

---

## PARTE 4: TESTAR AS FUNCIONALIDADES 🧪

Agora que o projeto está ligado, vamos testar! Abra um **TERCEIRO TERMINAL**.

### Comando Base
Todos os comandos seguem este padrão:
```bash
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "SUA MENSAGEM AQUI", "sender": "richel"}'
```

---

### ✅ TESTE 1: Salvar uma nota

**Situação:** Você quer guardar uma lembrança sobre tarefas da academia.

**Comando:**
```bash
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "salva: repor 3 halteres de 10kg até segunda", "sender": "richel"}'
```

**O que vai acontecer:**
1. A IA vai entender que você quer SALVAR algo
2. Vai criar uma nota no Obsidian automaticamente
3. Você vai ver algo assim na resposta:
```
✅ Nota criada com sucesso!
Categoria: Tarefas
Tag: #academia
Prioridade: alta
```

**Onde a nota fica:** `/Users/richelcalazans/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecCerebro/Tarefas/`

---

### ✅ TESTE 2: Buscar notas antigas

**Situação:** Você quer achar anotações sobre equipamentos.

**Comando:**
```bash
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "busca: equipamentos", "sender": "richel"}'
```

**O que vai acontecer:**
1. A IA procura entre suas notas antigas
2. Encontra todas com a palavra "equipamentos"
3. Mostra um resumo de cada uma

---

### ✅ TESTE 3: Pedir um resumo da semana

**Situação:** Você quer saber tudo que anotou essa semana.

**Comando:**
```bash
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "resumo da semana", "sender": "richel"}'
```

**O que vai acontecer:**
1. A IA lê TODAS as notas da semana
2. Faz um resumo bonito
3. Agrupa por categoria

---

### ✅ TESTE 4: Health Check (é só para verificar se está vivo)

**Situação:** Você quer confirmar que o servidor está funcionando.

**Comando:**
```bash
curl http://127.0.0.1:5000/health
```

**O que você deve ver:**
```json
{
  "status": "ok",
  "modelo": "gemma4:e4b",
  "timestamp": "2025-04-05T10:30:45"
}
```

---

## PARTE 5: LER OS LOGS 📖

Os logs são registros de tudo o que acontece. Muito útil quando algo dá errado.

### Onde ficam os logs
```
/Users/richelcalazans/agente_allpfit/agente_allpfit/logs/
```

### Como ler (terminal)

**Ver os últimas 20 linhas:**
```bash
tail -20 /Users/richelcalazans/agente_allpfit/agente_allpfit/logs/agente.log
```

**Ver TUDO (útil quando o arquivo é pequeno):**
```bash
cat /Users/richelcalazans/agente_allpfit/agente_allpfit/logs/agente.log
```

**Ver em tempo real (conforme as coisas acontecem):**
```bash
tail -f /Users/richelcalazans/agente_allpfit/agente_allpfit/logs/agente.log
```
*(Pressione Ctrl+C para parar)*

### O que procurar nos logs
```
[INFO]    - Operação bem-sucedida
[WARNING] - Aviso, algo pode estar errado
[ERROR]   - Erro, algo deu ruim
```

**Exemplo de um log bom:**
```
2025-04-05 10:30:45,123 [INFO] Agente AllpFit iniciado | Modelo: gemma4:e4b | Vault: ...
2025-04-05 10:31:02,456 [INFO] Mensagem recebida: "salva: repor halteres"
2025-04-05 10:31:05,789 [INFO] Nota criada: Tarefas/halteres.md
```

---

## PARTE 6: RESOLVER PROBLEMAS 🔧

### ❌ Problema: "Ollama não está rodando"

**O que aparece:**
```
[AVISO] Ollama não detectado. Inicie com: ollama serve
```

**Solução:**
1. Abra um terminal separado
2. Execute: `ollama serve`
3. Deixe rodando

---

### ❌ Problema: "Não consegue salvar a nota"

**Possível causa:** Obsidian não está configurado corretamente.

**Verifique:**
```bash
ls -la "/Users/richelcalazans/Library/Mobile Documents/iCloud~md~obsidian/Documents/SecCerebro/"
```

Se aparecer um erro, significa o caminho está errado. Edite o `config.yaml`:
```bash
nano /Users/richelcalazans/agente_allpfit/agente_allpfit/config.yaml
```

Encontre a linha `vault_path` e coloque o caminho correto.

---

### ❌ Problema: "Porta 5000 já está em uso"

**O que aparece:**
```
Address already in use
```

**Solução:**
```bash
# Ver o que está usando a porta 5000
lsof -i :5000

# Matar o processo (cuidado!)
kill -9 PID
```

---

### ❌ Problema: Agente não responde

**Primeira coisa a fazer:**
1. Verifique se Ollama está rodando (outro terminal com `ollama serve`)
2. Veja os logs: `tail -50 logs/agente.log`
3. Procure por `[ERROR]`

---

## PARTE 7: COMANDOS ÚTEIS DO DIA A DIA 📝

Copie esses para seus favoritos:

**Parar tudo:**
```bash
# No terminal que está rodando o agente: Ctrl+C
# No terminal do Ollama: Ctrl+C
```

**Ligar novamente (depois que parou):**
```bash
cd /Users/richelcalazans/agente_allpfit/agente_allpfit
bash scripts/start.sh
```

**Ver status rápido:**
```bash
curl http://127.0.0.1:5000/health
```

**Salvar uma nota rápido:**
```bash
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "salva: [sua mensagem]", "sender": "richel"}'
```

---

## ⏰ PRÓXIMOS PASSOS

1. **Hoje:** Siga este guia até conseguir ligar tudo
2. **Amanhã:** Acostume com os comandos, teste bastante
3. **Futura:** Quando quiser conectar WhatsApp, me avise (é outra configuração)

---

## 🆘 PRECISA DE AJUDA?

- Se um comando não funciona, veja a resposta exata do terminal
- Procure no arquivo de logs (seção "Ler logs")
- Se não conseguir resolver, me mostre a mensagem de erro completa

---

## 📚 RESUMO DE ARQUIVOS IMPORTANTES

| Arquivo | Para quê | Pode mexer? |
|---------|----------|------------|
| `config.yaml` | Configura IA, Obsidian, porta | ⚠️ Com cuidado |
| `agente.py` | Arquivo principal | ❌ Não |
| `scripts/start.sh` | Inicia tudo | ❌ Não |
| `logs/agente.log` | Registra tudo | ✅ Só ler |

---

**Boa sorte! Você consegue! 💪**
*- Claude, seu assistente*
