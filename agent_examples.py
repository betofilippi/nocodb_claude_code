"""
Exemplos de como diferentes tipos de agentes podem usar o NocoDB Gateway
"""

# 1. Agente Python Simples
import requests

class SimpleAgent:
    def __init__(self, agent_id="simple_agent"):
        self.agent_id = agent_id
        self.gateway_url = "http://localhost:8000/agent/execute"
    
    def query_nocodb(self, operation, args={}):
        response = requests.post(self.gateway_url, json={
            "agent_id": self.agent_id,
            "operation": operation,
            "args": args,
            "return_format": "structured"
        })
        return response.json()
    
    # Exemplo de uso
    def list_all_data(self):
        bases = self.query_nocodb("list_bases")
        for base in bases.get("items", []):
            print(f"Base: {base['title']}")
            tables = self.query_nocodb("list_tables", {"base_id": base["id"]})
            for table in tables.get("items", []):
                print(f"  Tabela: {table['title']}")

# 2. Agente com LangChain
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI

def nocodb_tool_wrapper(query):
    """Wrapper para LangChain"""
    parts = query.split(" ", 1)
    operation = parts[0]
    args = eval(parts[1]) if len(parts) > 1 else {}
    
    response = requests.post("http://localhost:8000/agent/execute", json={
        "agent_id": "langchain_agent",
        "operation": operation,
        "args": args
    })
    return str(response.json())

nocodb_tool = Tool(
    name="NocoDB",
    func=nocodb_tool_wrapper,
    description="Acessa dados do NocoDB. Use: operation {args}"
)

# Agente LangChain
llm = OpenAI(temperature=0)
agent = initialize_agent([nocodb_tool], llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

# 3. Agente Assíncrono
import asyncio
import aiohttp

class AsyncAgent:
    def __init__(self, agent_id="async_agent"):
        self.agent_id = agent_id
        self.gateway_url = "http://localhost:8000/agent/execute"
    
    async def query_nocodb(self, operation, args={}):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.gateway_url, json={
                "agent_id": self.agent_id,
                "operation": operation,
                "args": args
            }) as response:
                return await response.json()
    
    async def parallel_queries(self):
        """Executa múltiplas queries em paralelo"""
        tasks = [
            self.query_nocodb("list_bases"),
            self.query_nocodb("list_tables", {"base_id": "base_id_here"}),
        ]
        results = await asyncio.gather(*tasks)
        return results

# 4. Agente com WebSocket
import websockets
import json

class StreamingAgent:
    def __init__(self, agent_id="streaming_agent"):
        self.agent_id = agent_id
        self.ws_url = "ws://localhost:8000/agent/stream"
    
    async def stream_operations(self):
        async with websockets.connect(self.ws_url) as websocket:
            # Enviar operação
            await websocket.send(json.dumps({
                "operation": "list_bases",
                "args": {}
            }))
            
            # Receber resposta
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Recebido: {data}")
            
            # Continuar com outras operações...
            for base in data.get("result", {}).get("list", []):
                await websocket.send(json.dumps({
                    "operation": "list_tables",
                    "args": {"base_id": base["id"]}
                }))
                tables = await websocket.recv()
                print(f"Tabelas de {base['title']}: {tables}")

# 5. Agente com Cache
class CachedAgent:
    def __init__(self, agent_id="cached_agent"):
        self.agent_id = agent_id
        self.gateway_url = "http://localhost:8000/agent/execute"
        self.local_cache = {}
    
    def query_nocodb(self, operation, args={}, use_cache=True):
        cache_key = f"{operation}:{json.dumps(args)}"
        
        # Verificar cache local primeiro
        if use_cache and cache_key in self.local_cache:
            return self.local_cache[cache_key]
        
        # Fazer requisição (o gateway também tem cache)
        response = requests.post(self.gateway_url, json={
            "agent_id": self.agent_id,
            "operation": operation,
            "args": args
        })
        
        data = response.json()
        
        # Salvar no cache local
        if use_cache:
            self.local_cache[cache_key] = data
        
        return data

# 6. Agente Batch
class BatchAgent:
    def __init__(self, agent_id="batch_agent"):
        self.agent_id = agent_id
        self.batch_url = "http://localhost:8000/agent/batch"
    
    def batch_operations(self, operations):
        """Executa múltiplas operações em uma única requisição"""
        response = requests.post(self.batch_url, json={
            "requests": operations,
            "parallel": True
        })
        return response.json()
    
    def example_batch(self):
        operations = [
            {"operation": "list_bases", "args": {}},
            {"operation": "list_tables", "args": {"base_id": "some_id"}},
            {"operation": "create_record", "args": {
                "table_id": "table_id",
                "record_data": {"name": "Test"}
            }}
        ]
        return self.batch_operations(operations)

# 7. Agente com Processamento de Linguagem Natural
class NLPAgent:
    def __init__(self, agent_id="nlp_agent"):
        self.agent_id = agent_id
        self.gateway_url = "http://localhost:8000/agent/execute"
    
    def process_natural_language(self, user_input):
        """Converte linguagem natural em operações NocoDB"""
        # Mapeamento simples (em produção, use NLP real)
        if "listar bases" in user_input.lower():
            return self.query_nocodb("list_bases")
        elif "criar registro" in user_input.lower():
            # Extrair informações do texto...
            return self.query_nocodb("create_record", {
                "table_id": "extracted_table_id",
                "record_data": {"name": "extracted_name"}
            })
    
    def query_nocodb(self, operation, args={}):
        response = requests.post(self.gateway_url, json={
            "agent_id": self.agent_id,
            "operation": operation,
            "args": args,
            "return_format": "text"  # Retorna como texto para NLP
        })
        return response.json()

# Exemplo de uso integrado
if __name__ == "__main__":
    # 1. Agente simples
    simple = SimpleAgent()
    bases = simple.query_nocodb("list_bases")
    print("Bases encontradas:", bases)
    
    # 2. Agente assíncrono
    async def test_async():
        agent = AsyncAgent()
        results = await agent.parallel_queries()
        print("Resultados paralelos:", results)
    
    # asyncio.run(test_async())
    
    # 3. Agente com cache
    cached = CachedAgent()
    # Primeira chamada - vai ao servidor
    result1 = cached.query_nocodb("list_bases")
    # Segunda chamada - pega do cache
    result2 = cached.query_nocodb("list_bases")
    
    # 4. Agente batch
    batch = BatchAgent()
    batch_results = batch.example_batch()
    print("Operações em batch:", batch_results)