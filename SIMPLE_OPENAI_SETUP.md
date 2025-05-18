# Configuração Simples - OpenAI Assistant + NocoDB

**Importante**: O OpenAI Assistant chama DIRETAMENTE o servidor no Railway. Não precisa de código Python!

## Passo 1: Criar Action no OpenAI Assistant

1. Acesse: https://platform.openai.com/assistants
2. Crie um novo Assistant
3. Vá em "Actions" (não "Functions")
4. Clique em "Create action"
5. Cole este schema:

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
                args:
                  type: object
              required:
                - tool
                - args
      responses:
        '200':
          description: Success
```

## Passo 2: Configurar Instruções

Cole estas instruções no campo "Instructions" do Assistant:

```
Você tem acesso ao NocoDB através da action nocodb_execute.

Operações principais:
- list_bases: Lista todos os projetos
- list_tables: Lista tabelas de um projeto (precisa base_id)
- list_records: Lista registros de uma tabela (precisa table_id)
- create_record: Cria novo registro (precisa table_id e record_data)
- update_record: Atualiza registro (precisa table_id, record_id e record_data)
- delete_record: Remove registro (precisa table_id e record_id)

Exemplos de uso:
1. Para listar projetos: use tool="list_bases" com args={}
2. Para criar registro: use tool="create_record" com args={"table_id": "xxx", "record_data": {"campo": "valor"}}
3. Para buscar registros: use tool="list_records" com args={"table_id": "xxx", "limit": 10}

Sempre explique o que está fazendo e mostre os resultados de forma clara.
```

## Passo 3: Testar

No playground do Assistant, teste com:

"Liste todos os projetos do NocoDB"

O Assistant vai automaticamente:
1. Chamar nocodb_execute com tool="list_bases" e args={}
2. Receber a resposta
3. Mostrar os projetos encontrados

## Exemplos de Conversas

### Exemplo 1: Listar Projetos
```
Usuário: Liste os projetos disponíveis
Assistant: Vou listar todos os projetos do NocoDB.

[Chama automaticamente a action]

Encontrei 6 projetos:
1. projeto_Estoque_Local
2. importacao.app
3. Base_Developer_Estoque
4. Base_Testes_Jorge
5. Supabase
6. Base_Estoque
```

### Exemplo 2: Criar Registro
```
Usuário: Crie um novo cliente chamado João Silva
Assistant: Para criar um novo cliente, preciso saber em qual tabela. 
Você pode me informar o ID da tabela de clientes?

Usuário: Use a tabela "tbl_clientes_123"
Assistant: Vou criar o registro do cliente João Silva.

[Chama action com tool="create_record"]

Cliente criado com sucesso!
- Nome: João Silva
- ID do registro: rec_abc123
```

## Todas as Operações Disponíveis

```
Bases: list_bases, get_base, create_base, update_base, delete_base
Tabelas: list_tables, get_table, create_table, update_table, delete_table
Colunas: list_columns, create_column, update_column, delete_column
Registros: list_records, get_record, create_record, update_record, delete_record
Em lote: bulk_create_records, bulk_update_records, bulk_delete_records
Views: list_views, create_view, update_view, delete_view
Filtros: list_filters, create_filter, update_filter, delete_filter
Ordenação: list_sorts, create_sort, update_sort, delete_sort
Compartilhamento: create_shared_view, update_shared_view, delete_shared_view
Webhooks: list_webhooks, create_webhook, update_webhook, delete_webhook
Busca: global_search
Comentários: list_comments, create_comment, update_comment, delete_comment
Arquivos: upload_file
```

## Pronto! 🎉

Seu Assistant está configurado para usar o NocoDB diretamente, sem necessidade de código!