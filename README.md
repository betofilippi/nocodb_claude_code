# NocoDB MCP Server

Servidor MCP (Model Context Protocol) completo para integração com NocoDB API v2.

🚀 **Agora com suporte para HTTP REST API para deploy no Railway!**

## Features

✨ **Gerenciamento completo de bases, tabelas e registros**
📊 **Suporte para views, filtros e ordenação**
🔄 **Operações em lote (bulk operations)**
🔗 **Webhooks e compartilhamento**
🔍 **Pesquisa global**
💬 **Sistema de comentários**
📎 **Upload de arquivos**

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/betofilippi/nocodb_mcp_full.git
cd nocodb_mcp_full
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:
```
NOCODB_BASE_URL=https://nocodb.plataforma.app/api/v2
NOCODB_API_KEY=SEU_TOKEN_AQUI
```

### 4. Adicione o servidor ao Claude

```bash
claude mcp add nocodb -- python3 /caminho/completo/para/mcp_nocodb_server_full.py
```

## Ferramentas Disponíveis

### Gerenciamento de Bases
- `list_bases`: Listar todas as bases
- `get_base`: Obter detalhes de uma base
- `create_base`: Criar nova base
- `update_base`: Atualizar base
- `delete_base`: Deletar base

### Gerenciamento de Tabelas
- `list_tables`: Listar tabelas de uma base
- `get_table`: Obter detalhes de uma tabela
- `create_table`: Criar nova tabela
- `update_table`: Atualizar tabela
- `delete_table`: Deletar tabela

### Gerenciamento de Colunas
- `list_columns`: Listar colunas de uma tabela
- `create_column`: Criar nova coluna
- `update_column`: Atualizar coluna
- `delete_column`: Deletar coluna

### Gerenciamento de Registros
- `list_records`: Listar registros com paginação e filtros
- `get_record`: Obter registro específico
- `create_record`: Criar novo registro
- `update_record`: Atualizar registro
- `delete_record`: Deletar registro
- `bulk_create_records`: Criar múltiplos registros
- `bulk_update_records`: Atualizar múltiplos registros
- `bulk_delete_records`: Deletar múltiplos registros

### Gerenciamento de Views
- `list_views`: Listar views de uma tabela
- `create_view`: Criar nova view
- `update_view`: Atualizar view
- `delete_view`: Deletar view

### Filtros e Ordenação
- `create_filter`: Criar filtro para uma view
- `create_sort`: Criar ordenação para uma view

### Webhooks
- `list_webhooks`: Listar webhooks de uma tabela
- `create_webhook`: Criar novo webhook

### Outras Funcionalidades
- `share_view`: Compartilhar view publicamente
- `global_search`: Pesquisar em todas as tabelas
- `add_comment`: Adicionar comentário a um registro
- `upload_file`: Fazer upload de arquivo

## Exemplos de Uso

### Listar bases
```python
mcp.nocodb.list_bases()
```

### Criar nova tabela
```python
mcp.nocodb.create_table(
    base_id="p1sg177yxvrkbdq",
    title="Clientes",
    columns=[
        {"title": "Nome", "uidt": "SingleLineText"},
        {"title": "Email", "uidt": "Email"},
        {"title": "Telefone", "uidt": "PhoneNumber"}
    ]
)
```

### Pesquisar registros
```python
mcp.nocodb.list_records(
    table_id="mcf24tab2j5yx2o",
    limit=10,
    where="(Nome,eq,João)",
    sort="-created_at"
)
```

### Criar registro
```python
mcp.nocodb.create_record(
    table_id="mcf24tab2j5yx2o",
    data={
        "Nome": "João Silva",
        "Email": "joao@email.com",
        "Telefone": "+55 11 98765-4321"
    }
)
```

### Operações em lote
```python
mcp.nocodb.bulk_create_records(
    table_id="mcf24tab2j5yx2o",
    records=[
        {"Nome": "Ana", "Email": "ana@email.com"},
        {"Nome": "Carlos", "Email": "carlos@email.com"},
        {"Nome": "Maria", "Email": "maria@email.com"}
    ]
)
```

### Criar webhook
```python
mcp.nocodb.create_webhook(
    table_id="mcf24tab2j5yx2o",
    title="Notificar novo cliente",
    event="insert",
    url="https://seu-webhook.com/novo-cliente"
)
```

## Desenvolvimento

### Estrutura do projeto
```
nocodb_mcp_full/
├── mcp_nocodb_server_full.py   # Servidor MCP completo
├── mcp_nocodb_server.py        # Servidor MCP básico
├── main.py                     # API FastAPI auxiliar
├── requirements.txt            # Dependências
├── README.md                   # Documentação
├── LICENSE                     # Licença MIT
├── .env.example               # Exemplo de configuração
└── .gitignore                 # Arquivos ignorados
```

### Executar em modo desenvolvimento
```bash
python3 mcp_nocodb_server_full.py
```

### Debug com MCP
```bash
claude --mcp-debug
```

## Configuração MCP

### Escopo local (apenas este projeto)
```bash
claude mcp add nocodb -- python3 /caminho/para/mcp_nocodb_server_full.py
```

### Escopo global (todos os projetos)
```bash
claude mcp add -s user nocodb -- python3 /caminho/para/mcp_nocodb_server_full.py
```

### Escopo de projeto (compartilhado via .mcp.json)
```bash
claude mcp add -s project nocodb -- python3 /caminho/para/mcp_nocodb_server_full.py
```

## Deploy HTTP Server (Railway)

Este projeto inclui uma versão HTTP REST API que pode ser deployada em plataformas como Railway.

### Arquivos Incluídos

- `nocodb_http_server.py` - Servidor HTTP com FastAPI
- `Dockerfile` - Para containerização
- `railway.toml` - Configuração do Railway
- `API_DOCUMENTATION.md` - Documentação completa da API

### Deploy no Railway

1. Fork este repositório
2. Conecte ao Railway via GitHub
3. Configure as variáveis de ambiente:
   - `NOCODB_BASE_URL`
   - `NOCODB_API_KEY`
4. Deploy automático

### Endpoints

- `GET /` - Informações do servidor
- `GET /health` - Health check
- `GET /tools` - Lista todas as ferramentas disponíveis
- `POST /execute` - Executa uma ferramenta

### Exemplo de uso

```bash
curl -X POST https://seu-app.railway.app/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "list_bases",
    "args": {}
  }'
```

## Segurança

- **Nunca commite seu token de API**: Use variáveis de ambiente
- **Use .gitignore**: Garanta que `.env` não seja commitado
- **Tokens seguros**: Gere tokens específicos para o MCP com permissões limitadas
- **HTTPS**: Todo tráfego é criptografado

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commite suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

MIT - veja [LICENSE](LICENSE) para detalhes