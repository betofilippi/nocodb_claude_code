# Configuração do NocoDB Tool no OpenAI Assistant

## 1. Definição da Função

Use a seguinte definição de função ao criar seu Assistant no playground da OpenAI:

```json
{
  "name": "nocodb_execute",
  "description": "Execute operations on NocoDB database through a REST API server. This tool provides comprehensive access to NocoDB features including bases, tables, records, views, filters, webhooks, and more.",
  "parameters": {
    "type": "object",
    "properties": {
      "tool": {
        "type": "string",
        "description": "The NocoDB operation to execute",
        "enum": [
          "list_bases", "get_base", "create_base", "update_base", "delete_base",
          "list_tables", "get_table", "create_table", "update_table", "delete_table",
          "list_columns", "create_column", "update_column", "delete_column",
          "list_records", "get_record", "create_record", "update_record", "delete_record",
          "bulk_create_records", "bulk_update_records", "bulk_delete_records",
          "list_views", "create_view", "update_view", "delete_view",
          "list_filters", "create_filter", "update_filter", "delete_filter",
          "list_sorts", "create_sort", "update_sort", "delete_sort",
          "create_shared_view", "update_shared_view", "delete_shared_view",
          "list_webhooks", "create_webhook", "update_webhook", "delete_webhook",
          "global_search", "list_comments", "create_comment", "update_comment", 
          "delete_comment", "upload_file"
        ]
      },
      "args": {
        "type": "object",
        "description": "The arguments specific to each tool operation"
      }
    },
    "required": ["tool", "args"]
  }
}
```

## 2. Implementação da Função

No seu código Python/Node.js/etc, implemente a função que fará a chamada HTTP:

### Python Example

```python
import requests
import json

def nocodb_execute(tool, args):
    """Execute NocoDB operations via HTTP API"""
    
    url = "https://nocodbclaudecode-production.up.railway.app/execute"
    
    payload = {
        "tool": tool,
        "args": args
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
```

### Node.js Example

```javascript
async function nocodb_execute(tool, args) {
    const url = 'https://nocodbclaudecode-production.up.railway.app/execute';
    
    const payload = {
        tool: tool,
        args: args
    };
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        return { error: error.message };
    }
}
```

## 3. Instruções do Sistema (System Prompt)

Adicione estas instruções ao seu Assistant:

```
Você tem acesso a um banco de dados NocoDB através da função nocodb_execute. 
Esta função permite realizar operações completas no banco de dados incluindo:

- Gerenciar bases/projetos (listar, criar, atualizar, deletar)
- Gerenciar tabelas (criar estruturas, modificar, deletar)
- Gerenciar colunas (adicionar campos, modificar tipos, remover)
- Gerenciar registros (CRUD completo, operações em lote)
- Criar e gerenciar views, filtros e ordenações
- Configurar webhooks e compartilhamentos
- Realizar buscas globais
- Gerenciar comentários em registros

Exemplos de uso:

1. Listar todas as bases:
nocodb_execute("list_bases", {})

2. Listar tabelas de uma base:
nocodb_execute("list_tables", {"base_id": "p1sg177yxvrkbdq"})

3. Criar um novo registro:
nocodb_execute("create_record", {
  "table_id": "table_id_aqui",
  "record_data": {
    "Nome": "João Silva",
    "Email": "joao@example.com"
  }
})

4. Buscar registros com filtro:
nocodb_execute("list_records", {
  "table_id": "table_id_aqui",
  "where": "(Status,eq,Ativo)",
  "limit": 10
})

Sempre forneça feedback claro sobre as operações realizadas e trate erros adequadamente.
```

## 4. Exemplos de Conversação

### Exemplo 1: Listar Projetos
```
Usuário: "Quais são os projetos disponíveis no NocoDB?"
Assistant: Vou listar os projetos disponíveis no NocoDB.

[Chama nocodb_execute("list_bases", {})]

Encontrei 6 projetos no NocoDB:

1. **projeto_Estoque_Local** - Criado em 12/05/2025
2. **importacao.app** - Atualizado em 17/05/2025
3. **Base_Developer_Estoque** - Criado em 13/05/2025
4. **Base_Testes_Jorge** - Criado em 13/05/2025
5. **Supabase** - Atualizado em 15/05/2025
6. **Base_Estoque** - Criado em 16/05/2025

Qual projeto você gostaria de explorar?
```

### Exemplo 2: Criar um Registro
```
Usuário: "Crie um novo cliente na tabela Clientes"
Assistant: Para criar um novo cliente, preciso de algumas informações. 
Quais dados você gostaria de incluir? (Nome, Email, Telefone, etc.)

Usuário: "Nome: Maria Silva, Email: maria@email.com, Telefone: 11999999999"
Assistant: Vou criar o registro do novo cliente.

[Chama nocodb_execute("create_record", {
  "table_id": "table_clientes_id",
  "record_data": {
    "Nome": "Maria Silva",
    "Email": "maria@email.com",
    "Telefone": "11999999999"
  }
})]

Cliente criado com sucesso! 
✅ Nome: Maria Silva
✅ Email: maria@email.com
✅ Telefone: 11999999999
```

## 5. Tratamento de Erros

Sempre implemente tratamento de erros adequado:

```python
def handle_nocodb_operation(tool, args):
    try:
        result = nocodb_execute(tool, args)
        
        if "error" in result:
            return f"❌ Erro ao executar operação: {result['error']}"
        
        if "result" in result:
            return result["result"]
        
        return result
        
    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"
```

## 6. Configuração no OpenAI Platform

1. Acesse https://platform.openai.com/playground
2. Crie um novo Assistant
3. Em "Tools", clique em "Add function"
4. Cole a definição da função `nocodb_execute`
5. Configure as instruções do sistema
6. Teste a integração

## 7. Variáveis de Ambiente

Se você estiver hospedando seu próprio servidor, configure:
- `NOCODB_BASE_URL`: URL da sua instância NocoDB
- `NOCODB_API_KEY`: Token de autenticação

## 8. Limitações e Considerações

- Rate limits do servidor (se aplicável)
- Tamanho máximo de payload
- Timeout de requisições
- Segurança: não exponha tokens em logs
- Validação de dados antes de enviar

## 9. Debugging

Para debug, você pode adicionar logs:

```python
import logging

logging.basicConfig(level=logging.INFO)

def nocodb_execute_debug(tool, args):
    logging.info(f"Executing tool: {tool}")
    logging.info(f"Arguments: {json.dumps(args, indent=2)}")
    
    result = nocodb_execute(tool, args)
    
    logging.info(f"Result: {json.dumps(result, indent=2)}")
    return result
```

## 10. Exemplos Avançados

### Busca com Filtros Complexos
```python
# Buscar registros com múltiplas condições
result = nocodb_execute("list_records", {
    "table_id": "table_id",
    "where": "(Status,eq,Ativo)~and(Valor,gt,1000)",
    "sort": ["-CreatedAt"],
    "limit": 50
})
```

### Operações em Lote
```python
# Criar múltiplos registros
result = nocodb_execute("bulk_create_records", {
    "table_id": "table_id",
    "records": [
        {"Nome": "Cliente 1", "Email": "cliente1@email.com"},
        {"Nome": "Cliente 2", "Email": "cliente2@email.com"},
        {"Nome": "Cliente 3", "Email": "cliente3@email.com"}
    ]
})
```

### Criar Tabela com Estrutura
```python
# Criar nova tabela
result = nocodb_execute("create_table", {
    "base_id": "base_id",
    "name": "Produtos",
    "columns": [
        {"name": "Nome", "type": "SingleLineText", "required": true},
        {"name": "Preço", "type": "Number"},
        {"name": "Categoria", "type": "SingleSelect"},
        {"name": "Em Estoque", "type": "Checkbox"}
    ]
})
```