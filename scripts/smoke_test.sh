#!/bin/bash
# Smoke test do Agente AllpFit

set -e

BASE_URL="http://127.0.0.1:5000"
PASSED=0
FAILED=0

echo "=================================================="
echo "  SMOKE TEST - Agente AllpFit"
echo "=================================================="

# Função auxiliar
check() {
    local desc="$1"
    local result="$2"
    local expected="$3"

    if echo "$result" | grep -q "$expected"; then
        echo "  [OK] $desc"
        PASSED=$((PASSED + 1))
    else
        echo "  [FALHOU] $desc"
        echo "    Esperado: $expected"
        echo "    Recebido: $result"
        FAILED=$((FAILED + 1))
    fi
}

# Verifica se o servidor está rodando
echo ""
echo "[1/4] Testando health check..."
HEALTH=$(curl -s "$BASE_URL/health" 2>/dev/null || echo "CONNECTION_ERROR")
if echo "$HEALTH" | grep -q "CONNECTION_ERROR"; then
    echo "  [ERRO] Servidor não está rodando em $BASE_URL"
    echo "  Inicie com: ./scripts/start.sh"
    exit 1
fi
check "Health check retorna status ok" "$HEALTH" '"status":"ok"'

echo ""
echo "[2/4] Testando stats..."
STATS=$(curl -s "$BASE_URL/stats")
check "Stats retorna notas_criadas" "$STATS" "notas_criadas"

echo ""
echo "[3/4] Testando webhook com mensagem simples..."
RESP=$(curl -s -X POST "$BASE_URL/webhook" \
    -H "Content-Type: application/json" \
    -d '{"text": "Oi, tudo bem?", "sender": "teste"}')
check "Webhook retorna sucesso" "$RESP" "sucesso"

echo ""
echo "[4/4] Testando webhook com pedido de nota..."
RESP=$(curl -s -X POST "$BASE_URL/webhook" \
    -H "Content-Type: application/json" \
    -d '{"text": "Salva isso: repor 3 halteres de 10kg até segunda", "sender": "teste"}')
check "Webhook processa pedido de nota" "$RESP" "sucesso"

echo ""
echo "=================================================="
echo "  RESULTADO: $PASSED passou, $FAILED falhou"
echo "=================================================="

if [ $FAILED -gt 0 ]; then
    exit 1
fi
