# Configuração Direta do NocoDB no OpenAI Assistant

O OpenAI Assistant vai chamar DIRETAMENTE o servidor no Railway. Você NÃO precisa de código Python ou qualquer outro intermediário.

## 1. Definição da Função (Copie e Cole no OpenAI)

```json
{
  "type": "function",
  "function": {
    "name": "nocodb_execute",
    "description": "Execute operations on NocoDB database",
    "parameters": {
      "type": "object",
      "properties": {
        "tool": {
          "type": "string",
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
          ],
          "description": "The NocoDB operation to execute"
        },
        "args": {
          "type": "object",
          "description": "Arguments for the operation"
        }
      },
      "required": ["tool", "args"]
    }
  }
}
```

## 2. Configurar o Action no OpenAI Assistant

No OpenAI Assistant Playground:

1. Crie um novo Assistant
2. Vá em "Actions" (não "Functions")
3. Clique em "Create action"
4. Configure:

### Schema da Action:

```yaml
openapi: 3.0.0
info:
  title: NocoDB API
  version: 1.0.0
servers:
  - url: https://nocodbclaudecode-production.up.railway.app
paths:
  /execute:
    post:
      summary: Execute NocoDB operation
      operationId: nocodb_execute
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                tool:
                  type: string
                  enum: 
                    - list_bases
                    - get_base
                    - create_base
                    - update_base
                    - delete_base
                    - list_tables
                    - get_table
                    - create_table
                    - update_table
                    - delete_table
                    - list_columns
                    - create_column
                    - update_column
                    - delete_column
                    - list_records
                    - get_record
                    - create_record
                    - update_record
                    - delete_record
                    - bulk_create_records
                    - bulk_update_records
                    - bulk_delete_records
                    - list_views
                    - create_view
                    - update_view
                    - delete_view
                    - list_filters
                    - create_filter
                    - update_filter
                    - delete_filter
                    - list_sorts
                    - create_sort
                    - update_sort
                    - delete_sort
                    - create_shared_view
                    - update_shared_view
                    - delete_shared_view
                    - list_webhooks
                    - create_webhook
                    - update_webhook
                    - delete_webhook
                    - global_search
                    - list_comments
                    - create_comment
                    - update_comment
                    - delete_comment
                    - upload_file
                args:
                  type: object
              required:
                - tool
                - args
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  result:
                    type: object
```

## 3. Instruções do Sistema

Adicione estas instruções ao seu Assistant:

```
Você tem acesso direto ao NocoDB através da action nocodb_execute. 
Esta action permite realizar operações completas no banco de dados.

Para usar:
1. Chame nocodb_execute com o parâmetro "tool" (operação desejada)
2. Passe os argumentos necessários em "args"

Exemplos:
- Listar bases: nocodb_execute com tool="list_bases" e args={}
- Criar registro: nocodb_execute com tool="create_record" e args={"table_id": "id", "record_data": {...}}
- Buscar registros: nocodb_execute com tool="list_records" e args={"table_id": "id", "where": "filtro"}

Operações disponíveis:
- Bases: list_bases, get_base, create_base, update_base, delete_base
- Tabelas: list_tables, get_table, create_table, update_table, delete_table
- Registros: list_records, get_record, create_record, update_record, delete_record
- Operações em lote: bulk_create_records, bulk_update_records, bulk_delete_records
- Views: list_views, create_view, update_view, delete_view
- Filtros e ordenação: list_filters, create_filter, list_sorts, create_sort
- Outros: global_search, list_comments, create_comment

Sempre forneça feedback claro sobre as operações realizadas.
```

## 4. Exemplo de Uso (Sem Código!)

Quando o usuário pedir algo, o Assistant vai:

**Usuário**: "Liste todas as bases do NocoDB"

**Assistant vai automaticamente**:
1. Chamar a action nocodb_execute
2. Com parâmetros: `{"tool": "list_bases", "args": {}}`
3. Receber a resposta do servidor Railway
4. Formatar e mostrar para o usuário

**Resposta do Assistant**:
"Encontrei 6 bases no NocoDB:
1. projeto_Estoque_Local
2. importacao.app
3. Base_Developer_Estoque
4. Base_Testes_Jorge
5. Supabase
6. Base_Estoque"

## 5. Configuração Completa

1. No OpenAI Assistant Playground
2. Crie novo Assistant
3. Adicione a Action com o schema acima
4. Configure as instruções
5. Teste diretamente - sem código necessário!

O Assistant vai chamar diretamente:
```
POST https://nocodbclaudecode-production.up.railway.app/execute
{
  "tool": "list_bases",
  "args": {}
}
```

E receber a resposta para processar e mostrar ao usuário.