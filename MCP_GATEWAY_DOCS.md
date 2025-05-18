# MCP Gateway Universal - Documentação

## Visão Geral

O MCP Gateway é uma solução para gerenciar múltiplos servidores MCP (Model Context Protocol) e expô-los via API REST unificada. Permite que agentes de IA e aplicações acessem diferentes serviços MCP através de uma interface consistente.

## Arquitetura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Agentes/Apps  │     │   MCP Gateway   │     │  MCP Servers    │
│                 │     │                 │     │                 │
│ • ChatBots      │────▶│ • API REST      │────▶│ • NocoDB        │
│ • AI Agents     │     │ • Router        │     │ • Filesystem    │
│ • Web Apps      │     │ • Manager       │     │ • GitHub        │
│ • Scripts       │     │ • Cache         │     │ • Memory        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Instalação

1. **Instalar dependências**:
```bash
pip install fastapi uvicorn pyyaml
```

2. **Configurar servidores MCP**:
Edite o arquivo `mcp_servers.yaml`:

```yaml
servers:
  - name: nocodb
    command: python /path/to/mcp_nocodb_server.py
    description: NocoDB Database Server
    env_vars:
      NOCODB_BASE_URL: https://nocodb.example.com/api/v2
      NOCODB_API_KEY: your_token
    enabled: true
    auto_start: true

  - name: filesystem
    command: mcp-server-filesystem
    description: File System Operations
    env_vars:
      ALLOWED_PATHS: /home/user/documents
    enabled: true
    auto_start: false
```

3. **Iniciar o Gateway**:
```bash
python mcp_gateway_simple.py
```

O gateway estará disponível em `http://localhost:8002`

## API Reference

### 1. Chamar ferramenta MCP

```http
POST /call
Content-Type: application/json

{
  "server": "nocodb",
  "tool": "list_bases",
  "args": {}
}
```

**Resposta**:
```json
{
  "server": "nocodb",
  "result": {
    "list": [
      {"id": "base1", "title": "My Database"}
    ]
  },
  "timestamp": "2024-01-20T10:30:00",
  "duration": 0.123
}
```

### 2. Listar servidores

```http
GET /servers
```

**Resposta**:
```json
{
  "servers": [
    {
      "name": "nocodb",
      "initialized": true,
      "running": true
    },
    {
      "name": "filesystem",
      "initialized": false,
      "running": false
    }
  ]
}
```

### 3. Status do Gateway

```http
GET /health
```

**Resposta**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00",
  "servers_count": 2,
  "servers": {
    "nocodb": true,
    "filesystem": false
  }
}
```

### 4. Atalhos para servidores específicos

```http
POST /nocodb/list_bases
Content-Type: application/json

{}
```

## Exemplos de Uso

### Python

```python
import requests

# Cliente simples
def call_mcp(server, tool, args={}):
    response = requests.post(
        "http://localhost:8002/call",
        json={"server": server, "tool": tool, "args": args}
    )
    return response.json()

# Usar
result = call_mcp("nocodb", "list_bases")
print(result)
```

### JavaScript

```javascript
async function callMCP(server, tool, args = {}) {
    const response = await fetch('http://localhost:8002/call', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({server, tool, args})
    });
    return response.json();
}

// Usar
const bases = await callMCP('nocodb', 'list_bases');
console.log(bases);
```

### cURL

```bash
curl -X POST http://localhost:8002/call \
  -H "Content-Type: application/json" \
  -d '{
    "server": "nocodb",
    "tool": "list_bases",
    "args": {}
  }'
```

## Adicionar Novos Servidores MCP

### 1. Editar configuração

Adicione ao `mcp_servers.yaml`:

```yaml
- name: meu_servidor
  command: python /path/to/meu_servidor_mcp.py
  description: Meu Servidor MCP
  env_vars:
    API_KEY: xxx
  enabled: true
```

### 2. Reiniciar Gateway

```bash
# Parar com Ctrl+C
# Iniciar novamente
python mcp_gateway_simple.py
```

### 3. Testar

```python
result = call_mcp("meu_servidor", "minha_ferramenta", {"param": "valor"})
```

## Desenvolvimento de Servidores MCP

Para criar um novo servidor MCP compatível:

```python
#!/usr/bin/env python3
import json
import sys
import logging

class MeuServidorMCP:
    def __init__(self):
        self.tools = {
            "minha_ferramenta": self.minha_ferramenta
        }
    
    def run(self):
        for line in sys.stdin:
            message = json.loads(line)
            response = self.handle_message(message)
            print(json.dumps(response))
            sys.stdout.flush()
    
    def handle_message(self, message):
        method = message.get("method")
        params = message.get("params", {})
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {}
                },
                "id": message["id"]
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "tools": [
                        {
                            "name": "minha_ferramenta",
                            "description": "Faz algo útil"
                        }
                    ]
                },
                "id": message["id"]
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name in self.tools:
                result = self.tools[tool_name](tool_args)
                return {
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": message["id"]
                }
    
    def minha_ferramenta(self, args):
        return {"resultado": "sucesso", "dados": args}

if __name__ == "__main__":
    server = MeuServidorMCP()
    server.run()
```

## Integração com Agentes de IA

### LangChain

```python
from langchain.tools import Tool
import requests

def mcp_tool(query):
    server, tool, *args = query.split()
    args_dict = eval(' '.join(args)) if args else {}
    
    response = requests.post(
        "http://localhost:8002/call",
        json={"server": server, "tool": tool, "args": args_dict}
    )
    return str(response.json())

langchain_tool = Tool(
    name="MCP_Gateway",
    func=mcp_tool,
    description="Acessa serviços MCP. Formato: server tool {args}"
)
```

### AutoGen

```python
class MCPAgent:
    def __init__(self):
        self.gateway_url = "http://localhost:8002"
    
    def call_mcp(self, server, tool, args={}):
        response = requests.post(
            f"{self.gateway_url}/call",
            json={"server": server, "tool": tool, "args": args}
        )
        return response.json()
```

## Monitoramento e Debug

### Logs

O gateway gera logs detalhados:

```python
# Configurar nível de log
logging.basicConfig(level=logging.DEBUG)
```

### Métricas

Adicione métricas customizadas:

```python
from prometheus_client import Counter, Histogram

mcp_calls = Counter('mcp_calls_total', 'Total MCP calls', ['server', 'tool'])
mcp_duration = Histogram('mcp_call_duration_seconds', 'MCP call duration')

# No handler
with mcp_duration.time():
    result = await manager.call_server(...)
mcp_calls.labels(server=server, tool=tool).inc()
```

## Deploy em Produção

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8002

CMD ["python", "mcp_gateway_simple.py"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-gateway
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mcp-gateway
  template:
    metadata:
      labels:
        app: mcp-gateway
    spec:
      containers:
      - name: gateway
        image: mcp-gateway:latest
        ports:
        - containerPort: 8002
        env:
        - name: LOG_LEVEL
          value: "INFO"
```

### Railway/Heroku

```yaml
# railway.yml
services:
  - name: mcp-gateway
    env:
      PORT: 8002
    build:
      dockerfile: Dockerfile
```

## Segurança

### Autenticação

Adicione autenticação JWT:

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Verificar token
    if not validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

@app.post("/call", dependencies=[Depends(verify_token)])
async def call_tool(request: MCPRequest):
    # ...
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/call")
@limiter.limit("100/minute")
async def call_tool(request: MCPRequest):
    # ...
```

## Troubleshooting

### Servidor MCP não responde

1. Verificar logs do gateway
2. Testar comando diretamente:
   ```bash
   python /path/to/mcp_server.py
   ```
3. Verificar variáveis de ambiente

### Erro de JSON

- Alguns servidores MCP incluem headers antes do JSON
- O gateway tenta encontrar o início do JSON automaticamente
- Se continuar falhando, ajuste o método `_read_response`

### Performance

- Use cache para requisições repetidas
- Configure pool de conexões
- Implemente circuit breaker para servidores instáveis

## Roadmap

- [ ] Interface Web para gerenciamento
- [ ] Suporte para WebSocket nativo
- [ ] Cache distribuído (Redis)
- [ ] Métricas Prometheus
- [ ] Dashboard Grafana
- [ ] Plugin system para transformações
- [ ] Suporte para gRPC

## Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -am 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## Licença

MIT - veja LICENSE para detalhes