#!/bin/bash
# Script de inicialização do Agente AllpFit

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=================================================="
echo "  AGENTE ALLPFIT - Iniciando..."
echo "=================================================="

# Verifica se o venv existe
if [ ! -d "venv" ]; then
    echo "[SETUP] Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativa o venv
source venv/bin/activate

# Instala dependências
echo "[SETUP] Verificando dependências..."
pip install -q -r requirements.txt

# Verifica se Ollama está rodando
echo "[CHECK] Verificando Ollama..."
if curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "[OK] Ollama está rodando"
else
    echo "[AVISO] Ollama não detectado. Inicie com: ollama serve"
    echo "        O agente vai funcionar, mas não conseguirá gerar respostas da IA."
fi

# Cria diretório de logs
mkdir -p logs

# Inicia o servidor
echo ""
echo "[START] Iniciando servidor na porta 5000..."
echo "        Envie mensagens com:"
echo '        curl -X POST http://127.0.0.1:5000/webhook \'
echo '          -H "Content-Type: application/json" \'
echo '          -d '"'"'{"text": "sua mensagem aqui", "sender": "richel"}'"'"''
echo ""

python agente.py
