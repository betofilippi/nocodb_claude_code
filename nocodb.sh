#!/bin/bash
# NocoDB CLI - Super simples!

API="https://nocodbclaudecode-production.up.railway.app/execute"

# Função para chamar API
nocodb() {
    local tool=$1
    local args=${2:-"{}"}
    
    curl -s -X POST "$API" \
        -H "Content-Type: application/json" \
        -d "{\"tool\": \"$tool\", \"args\": $args}" | jq
}

# Se executado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "$1" in
        bases)
            echo "Listando bases..."
            nocodb "list_bases"
            ;;
            
        tables)
            if [ -z "$2" ]; then
                echo "Uso: $0 tables <base_id>"
                exit 1
            fi
            echo "Listando tabelas da base $2..."
            nocodb "list_tables" "{\"base_id\": \"$2\"}"
            ;;
            
        records)
            if [ -z "$2" ]; then
                echo "Uso: $0 records <table_id> [limit]"
                exit 1
            fi
            limit=${3:-10}
            echo "Listando registros da tabela $2..."
            nocodb "list_records" "{\"table_id\": \"$2\", \"limit\": $limit}"
            ;;
            
        create)
            if [ -z "$2" ] || [ -z "$3" ]; then
                echo "Uso: $0 create <table_id> '<json_data>'"
                echo "Exemplo: $0 create tbl123 '{\"nome\": \"João\"}'"
                exit 1
            fi
            echo "Criando registro..."
            nocodb "create_record" "{\"table_id\": \"$2\", \"record_data\": $3}"
            ;;
            
        *)
            echo "NocoDB CLI"
            echo "Uso: $0 <comando> [argumentos]"
            echo ""
            echo "Comandos:"
            echo "  bases                    - Lista todas as bases"
            echo "  tables <base_id>         - Lista tabelas de uma base"
            echo "  records <table_id> [lim] - Lista registros de uma tabela"
            echo "  create <table_id> <json> - Cria novo registro"
            echo ""
            echo "Exemplos:"
            echo "  $0 bases"
            echo "  $0 tables base123"
            echo "  $0 records tbl456 20"
            echo "  $0 create tbl456 '{\"nome\":\"Maria\",\"email\":\"maria@email.com\"}'"
            ;;
    esac
fi

# Para usar como biblioteca:
# source nocodb.sh
# nocodb "list_bases"