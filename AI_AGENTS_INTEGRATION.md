# 🤖 Integração com Agentes de IA

## 1. LangChain (Popular para Agentes)

```python
# langchain_nocodb_tool.py
from langchain.tools import BaseTool
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from typing import Optional
import requests
import json

class NocoDBTool(BaseTool):
    name = "nocodb"
    description = "Interage com banco de dados NocoDB. Use para listar, criar, atualizar dados."
    
    def _run(self, query: str) -> str:
        """
        Formato do query: <operation> <args_json>
        Exemplo: "list_bases {}" ou "create_record {'table_id': 'x', 'record_data': {}}"
        """
        try:
            parts = query.split(' ', 1)
            operation = parts[0]
            args = json.loads(parts[1]) if len(parts) > 1 else {}
            
            response = requests.post(
                'https://nocodbclaudecode-production.up.railway.app/execute',
                json={'tool': operation, 'args': args}
            )
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            return f"Erro: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)

# Configurar agente
llm = OpenAI(temperature=0)
tools = [NocoDBTool()]
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

# Usar
response = agent.run("Liste todas as bases do NocoDB")
print(response)
```

## 2. AutoGen (Microsoft)

```python
# autogen_nocodb_agent.py
from autogen import AssistantAgent, UserProxyAgent
import requests
import json

class NocoDBAgent:
    def __init__(self):
        self.api_url = 'https://nocodbclaudecode-production.up.railway.app/execute'
        
        # Configurar agente assistente
        self.assistant = AssistantAgent(
            name="nocodb_assistant",
            system_message="""Você é um assistente que gerencia o NocoDB.
            Quando precisar de dados, use a função nocodb_execute.
            Operações disponíveis: list_bases, list_tables, create_record, etc.""",
            llm_config={"model": "gpt-4"},
        )
        
        # Configurar proxy do usuário
        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            code_execution_config={"work_dir": "coding"},
        )
        
        # Registrar função
        self.user_proxy.register_function(
            function_map={"nocodb_execute": self.nocodb_execute}
        )
    
    def nocodb_execute(self, operation: str, args: dict = {}) -> dict:
        """Executa operação no NocoDB"""
        response = requests.post(
            self.api_url,
            json={'tool': operation, 'args': args}
        )
        return response.json()
    
    def chat(self, message: str):
        self.user_proxy.initiate_chat(
            self.assistant,
            message=message
        )

# Usar
agent = NocoDBAgent()
agent.chat("Liste todas as bases do NocoDB e me diga quantas existem")
```

## 3. CrewAI (Multi-agentes)

```python
# crewai_nocodb.py
from crewai import Agent, Task, Crew
import requests
import json

class NocoDBTools:
    @staticmethod
    def execute(operation: str, args: dict = {}) -> str:
        """Executa operação no NocoDB"""
        response = requests.post(
            'https://nocodbclaudecode-production.up.railway.app/execute',
            json={'tool': operation, 'args': args}
        )
        return json.dumps(response.json(), indent=2)

# Criar agentes
data_analyst = Agent(
    role='Data Analyst',
    goal='Analisar dados do NocoDB',
    backstory='Especialista em análise de dados',
    tools=[NocoDBTools.execute],
    verbose=True
)

data_manager = Agent(
    role='Data Manager',
    goal='Gerenciar registros no NocoDB',
    backstory='Especialista em gerenciamento de dados',
    tools=[NocoDBTools.execute],
    verbose=True
)

# Criar tarefas
analyze_task = Task(
    description="Liste todas as bases e tabelas do NocoDB e faça um resumo",
    agent=data_analyst
)

create_task = Task(
    description="Crie um novo registro de teste em uma tabela",
    agent=data_manager
)

# Criar crew
crew = Crew(
    agents=[data_analyst, data_manager],
    tasks=[analyze_task, create_task],
    verbose=True
)

# Executar
result = crew.kickoff()
print(result)
```

## 4. Semantic Kernel (Microsoft)

```python
# semantic_kernel_nocodb.py
import semantic_kernel as sk
from semantic_kernel.skill_definition import sk_function
import requests
import json

class NocoDBSkill:
    @sk_function(
        description="Executa operações no NocoDB",
        name="nocodb_execute"
    )
    def execute(self, operation: str, args: str = "{}") -> str:
        """Executa operação no NocoDB"""
        args_dict = json.loads(args)
        response = requests.post(
            'https://nocodbclaudecode-production.up.railway.app/execute',
            json={'tool': operation, 'args': args_dict}
        )
        return json.dumps(response.json(), indent=2)

# Configurar kernel
kernel = sk.Kernel()
kernel.import_skill(NocoDBSkill(), "nocodb")

# Criar função semântica
sk_prompt = """
Liste as bases do NocoDB usando a função nocodb.
Depois, crie um resumo das bases encontradas.
"""

list_function = kernel.create_semantic_function(sk_prompt)
result = kernel.run_async(list_function).result
print(result)
```

## 5. Haystack (NLP Framework)

```python
# haystack_nocodb.py
from haystack import Pipeline
from haystack.nodes import PromptNode, PromptTemplate
import requests
import json

class NocoDBNode:
    def __init__(self):
        self.api_url = 'https://nocodbclaudecode-production.up.railway.app/execute'
    
    def run(self, operation: str, args: dict = {}):
        response = requests.post(
            self.api_url,
            json={'tool': operation, 'args': args}
        )
        return {"result": response.json()}

# Criar pipeline
template = PromptTemplate(
    prompt="""
    Analise os dados do NocoDB e forneça insights.
    Dados: {nocodb_data}
    
    Resposta:
    """,
    output_parser={"type": "str"}
)

nocodb_node = NocoDBNode()
prompt_node = PromptNode(
    model_name_or_path="gpt-3.5-turbo",
    default_prompt_template=template
)

pipeline = Pipeline()
pipeline.add_node(component=nocodb_node, name="NocoDB", inputs=["Query"])
pipeline.add_node(component=prompt_node, name="Prompt", inputs=["NocoDB"])

# Usar
result = pipeline.run(
    query="list_bases",
    params={
        "NocoDB": {"operation": "list_bases", "args": {}}
    }
)
```

## 6. Llama Index

```python
# llamaindex_nocodb.py
from llama_index import LLMPredictor, ServiceContext
from llama_index.tools import FunctionTool
from llama_index.agent import OpenAIAgent
import requests
import json

def nocodb_execute(operation: str, args: dict = {}) -> dict:
    """Executa operação no NocoDB"""
    response = requests.post(
        'https://nocodbclaudecode-production.up.railway.app/execute',
        json={'tool': operation, 'args': args}
    )
    return response.json()

# Criar ferramenta
nocodb_tool = FunctionTool.from_defaults(
    fn=nocodb_execute,
    name="nocodb",
    description="Executa operações no NocoDB"
)

# Criar agente
agent = OpenAIAgent.from_tools(
    [nocodb_tool],
    verbose=True
)

# Usar
response = agent.chat("Liste todas as bases do NocoDB")
print(response)
```

## 7. API REST para Qualquer Agente

```python
# universal_agent_api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

app = FastAPI()

class AgentRequest(BaseModel):
    operation: str
    args: dict = {}
    agent_context: dict = {}  # Contexto específico do agente

class NocoDBService:
    @staticmethod
    def execute(operation: str, args: dict):
        response = requests.post(
            'https://nocodbclaudecode-production.up.railway.app/execute',
            json={'tool': operation, 'args': args}
        )
        return response.json()

@app.post("/agent/nocodb")
async def nocodb_agent_endpoint(request: AgentRequest):
    """Endpoint universal para qualquer agente"""
    try:
        result = NocoDBService.execute(request.operation, request.args)
        
        # Adicionar contexto do agente se necessário
        if request.agent_context:
            result["agent_context"] = request.agent_context
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/nocodb/operations")
async def list_operations():
    """Lista operações disponíveis"""
    return {
        "operations": [
            "list_bases", "get_base", "create_base",
            "list_tables", "create_table",
            "list_records", "create_record", "update_record",
            "bulk_operations", "global_search"
        ]
    }

# Executar: uvicorn universal_agent_api:app --reload
```

## 8. Integração com Dialogflow

```python
# dialogflow_nocodb.py
from google.cloud import dialogflow
import requests
import json

class DialogflowNocoDBWebhook:
    def __init__(self):
        self.api_url = 'https://nocodbclaudecode-production.up.railway.app/execute'
    
    def handle_webhook(self, request):
        """Processa webhook do Dialogflow"""
        intent_name = request.get('queryResult', {}).get('intent', {}).get('displayName')
        parameters = request.get('queryResult', {}).get('parameters', {})
        
        # Mapear intents para operações NocoDB
        intent_mapping = {
            'ListBases': 'list_bases',
            'CreateRecord': 'create_record',
            'SearchRecords': 'list_records'
        }
        
        operation = intent_mapping.get(intent_name)
        if not operation:
            return {"fulfillmentText": "Operação não reconhecida"}
        
        # Executar operação
        result = self.execute_nocodb(operation, parameters)
        
        # Formatar resposta
        return {
            "fulfillmentText": self.format_response(result),
            "payload": result
        }
    
    def execute_nocodb(self, operation, args):
        response = requests.post(
            self.api_url,
            json={'tool': operation, 'args': args}
        )
        return response.json()
    
    def format_response(self, data):
        # Formatar dados para resposta natural
        if 'result' in data and 'list' in data['result']:
            items = data['result']['list']
            return f"Encontrei {len(items)} itens"
        return json.dumps(data)
```

## 9. Exemplo de Orquestração

```python
# agent_orchestrator.py
from typing import Dict, Any, List
import asyncio
import aiohttp

class NocoDBOrchestrator:
    def __init__(self):
        self.api_url = 'https://nocodbclaudecode-production.up.railway.app/execute'
        self.agents = {}
    
    def register_agent(self, name: str, processor):
        """Registra um agente processador"""
        self.agents[name] = processor
    
    async def execute_nocodb(self, operation: str, args: dict):
        """Executa operação no NocoDB async"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                json={'tool': operation, 'args': args}
            ) as response:
                return await response.json()
    
    async def process_request(self, agent_name: str, request: Dict[str, Any]):
        """Processa requisição através do agente especificado"""
        if agent_name not in self.agents:
            return {"error": f"Agente {agent_name} não encontrado"}
        
        # Executar operação NocoDB
        operation = request.get('operation')
        args = request.get('args', {})
        nocodb_result = await self.execute_nocodb(operation, args)
        
        # Processar com agente específico
        agent_processor = self.agents[agent_name]
        final_result = await agent_processor(nocodb_result, request)
        
        return final_result

# Exemplo de uso
orchestrator = NocoDBOrchestrator()

# Registrar processador para agente de análise
async def analytics_processor(data, request):
    # Processar dados para análise
    return {"analysis": "Dados processados", "original": data}

orchestrator.register_agent("analytics", analytics_processor)

# Executar
result = asyncio.run(orchestrator.process_request(
    "analytics",
    {"operation": "list_bases", "args": {}}
))
```

## 🎯 Recomendações

1. **Para começar rápido**: Use LangChain ou Llama Index
2. **Para multi-agentes**: Use CrewAI ou AutoGen
3. **Para produção**: Crie API REST universal
4. **Para chatbots**: Integre com Dialogflow/Rasa

Todos esses exemplos conectam agentes de IA ao servidor NocoDB no Railway!