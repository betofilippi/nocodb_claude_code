"""
Gateway Universal para Agentes de IA + NocoDB
Qualquer agente pode usar este servidor como intermediário
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import requests
import asyncio
import aiohttp
from datetime import datetime
import json

app = FastAPI(title="NocoDB Agent Gateway", version="1.0.0")

# Configurações
NOCODB_API = "https://nocodbclaudecode-production.up.railway.app/execute"

# Modelos
class NocoDBRequest(BaseModel):
    operation: str
    args: Dict[str, Any] = {}
    
class AgentRequest(BaseModel):
    agent_id: str
    operation: str
    args: Dict[str, Any] = {}
    context: Optional[Dict[str, Any]] = {}
    return_format: str = "json"  # json, text, structured

class BatchRequest(BaseModel):
    requests: List[NocoDBRequest]
    parallel: bool = True

# Cache simples em memória
cache = {}
CACHE_TTL = 300  # 5 minutos

def get_cache_key(operation: str, args: dict) -> str:
    return f"{operation}:{json.dumps(args, sort_keys=True)}"

# Cliente NocoDB
class NocoDBClient:
    @staticmethod
    async def execute_async(operation: str, args: dict):
        """Executa operação async"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                NOCODB_API,
                json={'tool': operation, 'args': args}
            ) as response:
                return await response.json()
    
    @staticmethod
    def execute_sync(operation: str, args: dict):
        """Executa operação sync"""
        response = requests.post(
            NOCODB_API,
            json={'tool': operation, 'args': args}
        )
        return response.json()

# Endpoints principais
@app.get("/")
async def root():
    return {
        "service": "NocoDB Agent Gateway",
        "endpoints": {
            "/agent/execute": "Executa operação única",
            "/agent/batch": "Executa múltiplas operações",
            "/agent/operations": "Lista operações disponíveis",
            "/health": "Status do serviço"
        }
    }

@app.post("/agent/execute")
async def execute_for_agent(request: AgentRequest):
    """Endpoint principal para agentes executarem operações"""
    try:
        # Verificar cache
        cache_key = get_cache_key(request.operation, request.args)
        if cache_key in cache:
            cached_time, cached_data = cache[cache_key]
            if datetime.now().timestamp() - cached_time < CACHE_TTL:
                return format_response(cached_data, request.return_format)
        
        # Executar operação
        result = await NocoDBClient.execute_async(request.operation, request.args)
        
        # Salvar no cache
        cache[cache_key] = (datetime.now().timestamp(), result)
        
        # Adicionar contexto do agente
        if request.context:
            result["agent_context"] = {
                "agent_id": request.agent_id,
                "timestamp": datetime.now().isoformat(),
                **request.context
            }
        
        return format_response(result, request.return_format)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/batch")
async def batch_execute(batch: BatchRequest):
    """Executa múltiplas operações em batch"""
    try:
        if batch.parallel:
            # Executar em paralelo
            tasks = [
                NocoDBClient.execute_async(req.operation, req.args)
                for req in batch.requests
            ]
            results = await asyncio.gather(*tasks)
        else:
            # Executar sequencialmente
            results = []
            for req in batch.requests:
                result = await NocoDBClient.execute_async(req.operation, req.args)
                results.append(result)
        
        return {"results": results, "count": len(results)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/operations")
async def list_operations():
    """Lista todas as operações disponíveis com descrições"""
    return {
        "operations": {
            "bases": {
                "list_bases": "Lista todas as bases",
                "get_base": "Obtém detalhes de uma base",
                "create_base": "Cria nova base",
                "update_base": "Atualiza base existente",
                "delete_base": "Remove base"
            },
            "tables": {
                "list_tables": "Lista tabelas de uma base",
                "get_table": "Obtém detalhes de uma tabela",
                "create_table": "Cria nova tabela",
                "update_table": "Atualiza tabela",
                "delete_table": "Remove tabela"
            },
            "records": {
                "list_records": "Lista registros com filtros",
                "get_record": "Obtém registro específico",
                "create_record": "Cria novo registro",
                "update_record": "Atualiza registro",
                "delete_record": "Remove registro",
                "bulk_create_records": "Cria múltiplos registros",
                "bulk_update_records": "Atualiza múltiplos registros",
                "bulk_delete_records": "Remove múltiplos registros"
            },
            "search": {
                "global_search": "Busca global em todos os dados"
            }
        },
        "examples": {
            "list_bases": {
                "operation": "list_bases",
                "args": {}
            },
            "create_record": {
                "operation": "create_record",
                "args": {
                    "table_id": "tbl_123",
                    "record_data": {"name": "João", "email": "joao@email.com"}
                }
            }
        }
    }

@app.get("/health")
async def health_check():
    """Verifica status do serviço"""
    try:
        # Testar conexão com NocoDB
        result = NocoDBClient.execute_sync("list_bases", {})
        nocodb_status = "online" if "result" in result else "error"
    except:
        nocodb_status = "offline"
    
    return {
        "status": "healthy",
        "nocodb": nocodb_status,
        "cache_size": len(cache),
        "timestamp": datetime.now().isoformat()
    }

# Utilitários
def format_response(data: dict, format_type: str) -> Any:
    """Formata resposta conforme solicitado pelo agente"""
    if format_type == "text":
        return {"text": json.dumps(data, indent=2)}
    elif format_type == "structured":
        # Formato estruturado para processamento
        if "result" in data and "list" in data["result"]:
            return {
                "items": data["result"]["list"],
                "count": len(data["result"]["list"]),
                "metadata": data.get("pageInfo", {})
            }
        return data
    else:
        # JSON padrão
        return data

# Middleware para logging
@app.middleware("http")
async def log_requests(request, call_next):
    """Log de todas as requisições"""
    start_time = datetime.now()
    response = await call_next(request)
    duration = (datetime.now() - start_time).total_seconds()
    
    # Log básico (adicione seu sistema de log aqui)
    print(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    
    return response

# WebSocket para agentes em tempo real
from fastapi import WebSocket
import json

@app.websocket("/agent/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para comunicação em tempo real com agentes"""
    await websocket.accept()
    try:
        while True:
            # Receber mensagem do agente
            data = await websocket.receive_text()
            request = json.loads(data)
            
            # Processar requisição
            result = await NocoDBClient.execute_async(
                request.get("operation"),
                request.get("args", {})
            )
            
            # Enviar resposta
            await websocket.send_text(json.dumps(result))
    except Exception as e:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)