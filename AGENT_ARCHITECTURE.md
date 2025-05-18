# 🏗️ Arquitetura de Integração com Agentes de IA

## Visão Geral

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agentes IA    │    │  Gateway API    │    │  NocoDB Server  │
│                 │    │   (FastAPI)     │    │   (Railway)     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • LangChain     │───▶│ • /agent/exec   │───▶│ • /execute      │
│ • AutoGen       │    │ • /agent/batch  │    │                 │
│ • CrewAI        │    │ • Cache         │    │ • list_bases    │
│ • Custom Agents │    │ • WebSocket     │    │ • CRUD ops      │
│ • Dialogflow    │    │ • Rate Limit    │    │ • Bulk ops      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                                              │
         │                                              │
         └──────────────────────────────────────────────┘
                    Resposta Processada
```

## Componentes

### 1. Agentes de IA (Clientes)
- **Função**: Processam linguagem natural e lógica de negócio
- **Exemplos**: LangChain, AutoGen, CrewAI, agentes customizados
- **Comunicação**: HTTP REST ou WebSocket com o Gateway

### 2. Gateway API (Intermediário)
- **Função**: Ponte entre agentes e NocoDB
- **Features**:
  - Cache de respostas
  - Rate limiting
  - Autenticação de agentes
  - Transformação de dados
  - Logging e métricas
  - WebSocket para real-time

### 3. NocoDB Server (Dados)
- **Função**: Armazena e gerencia dados
- **Deploy**: Railway (já funcionando)
- **API**: REST com todas operações CRUD

## Fluxos de Comunicação

### Fluxo Básico (REST)
```
1. Agente envia requisição POST para Gateway
2. Gateway valida e adiciona contexto
3. Gateway chama NocoDB Server
4. Gateway processa resposta
5. Gateway retorna dados formatados para Agente
```

### Fluxo em Tempo Real (WebSocket)
```
1. Agente conecta via WebSocket
2. Agente envia operações em stream
3. Gateway processa e responde em tempo real
4. Conexão permanece aberta para múltiplas operações
```

### Fluxo Batch
```
1. Agente envia múltiplas operações
2. Gateway executa em paralelo ou sequencial
3. Gateway agregha resultados
4. Retorna todos resultados de uma vez
```

## Exemplos de Implementação

### Deploy do Gateway

```bash
# 1. Local
cd nocodb_gateway
pip install -r requirements.txt
uvicorn agent_gateway:app --reload

# 2. Docker
docker build -t nocodb-gateway .
docker run -p 8000:8000 nocodb-gateway

# 3. Railway/Heroku
# Use o Dockerfile incluído
```

### Configurar Agente LangChain

```python
from langchain.tools import Tool
import requests

def nocodb_tool(query):
    response = requests.post(
        "http://gateway-url/agent/execute",
        json={
            "agent_id": "langchain_01",
            "operation": query.split()[0],
            "args": eval(query.split()[1])
        }
    )
    return response.json()

tool = Tool(
    name="NocoDB",
    func=nocodb_tool,
    description="Database operations"
)
```

### Configurar Agente AutoGen

```python
from autogen import AssistantAgent
import requests

class NocoDBAssistant(AssistantAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gateway = "http://gateway-url/agent/execute"
    
    def query_nocodb(self, operation, args={}):
        return requests.post(self.gateway, json={
            "agent_id": self.name,
            "operation": operation,
            "args": args
        }).json()
```

## Vantagens desta Arquitetura

### 1. Desacoplamento
- Agentes não conhecem detalhes do NocoDB
- Fácil trocar backend sem afetar agentes
- Gateway pode adicionar features sem mudar agentes

### 2. Performance
- Cache reduz chamadas desnecessárias
- Batch operations para eficiência
- WebSocket para real-time

### 3. Segurança
- Gateway controla acesso
- Rate limiting por agente
- Logs centralizados

### 4. Escalabilidade
- Gateway pode ter múltiplas instâncias
- Load balancing entre gateways
- Cache distribuído possível

## Deployment Options

### Opção 1: Tudo em Railway
```yaml
services:
  - name: nocodb-server
    env: production
    
  - name: agent-gateway
    env: production
    envVars:
      NOCODB_URL: ${nocodb-server.url}
```

### Opção 2: Gateway Local + NocoDB Railway
- Gateway roda localmente
- Conecta ao NocoDB no Railway
- Bom para desenvolvimento

### Opção 3: Serverless
- Gateway em AWS Lambda/Vercel
- NocoDB no Railway
- Escala automaticamente

## Métricas e Monitoramento

O Gateway pode coletar:
- Requisições por agente
- Operações mais usadas
- Tempo de resposta
- Taxa de cache hit
- Erros por tipo

## Próximos Passos

1. **Deploy Gateway**: Escolha onde hospedar
2. **Configurar Agentes**: Use os exemplos
3. **Adicionar Features**:
   - Autenticação
   - Rate limiting
   - Métricas detalhadas
   - Transformações customizadas

## Exemplo Completo

```python
# Agente completo com gateway
class SmartAgent:
    def __init__(self):
        self.gateway = "http://localhost:8000"
        self.agent_id = "smart_agent_001"
    
    async def analyze_database(self):
        # 1. Listar bases
        bases = await self.query("list_bases")
        
        # 2. Para cada base, listar tabelas
        for base in bases['items']:
            tables = await self.query(
                "list_tables", 
                {"base_id": base['id']}
            )
            
            # 3. Analisar estrutura
            print(f"Base {base['title']} tem {len(tables['items'])} tabelas")
    
    async def query(self, operation, args={}):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.gateway}/agent/execute",
                json={
                    "agent_id": self.agent_id,
                    "operation": operation,
                    "args": args
                }
            ) as response:
                return await response.json()
```

Com esta arquitetura, qualquer agente de IA pode facilmente integrar com o NocoDB!