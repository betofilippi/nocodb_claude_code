"""
MCP Gateway Simplificado - Versão que funciona com stdio pipes
"""

import json
import asyncio
import subprocess
import sys
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging
from datetime import datetime
import yaml
import os
from pathlib import Path
import uuid

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Gateway", version="1.0.0")

# Modelos
class MCPRequest(BaseModel):
    server: str  # Nome do servidor MCP
    tool: str    # Nome da ferramenta/método
    args: Dict[str, Any] = {}
    
class MCPResponse(BaseModel):
    server: str
    result: Any
    timestamp: str
    duration: float

# Cliente MCP Simplificado
class MCPClient:
    def __init__(self, name: str, command: str, env_vars: Dict[str, str] = {}):
        self.name = name
        self.command = command
        self.env_vars = env_vars
        self.process = None
        self.initialized = False
    
    async def start(self):
        """Inicia o servidor MCP"""
        if self.process and self.process.poll() is None:
            return
        
        env = os.environ.copy()
        env.update(self.env_vars)
        
        self.process = subprocess.Popen(
            self.command.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=0
        )
        
        # Enviar inicialização
        await self._send_message({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {}
            },
            "id": "init_" + str(uuid.uuid4())
        })
        
        # Aguardar resposta de inicialização
        response = await self._read_response()
        logger.info(f"Servidor {self.name} inicializado: {response}")
        
        # Listar ferramentas disponíveis
        await self._send_message({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": "list_" + str(uuid.uuid4())
        })
        
        tools_response = await self._read_response()
        logger.info(f"Ferramentas disponíveis em {self.name}: {tools_response}")
        
        self.initialized = True
    
    async def call_tool(self, tool: str, args: Dict[str, Any]) -> Any:
        """Chama uma ferramenta no servidor MCP"""
        if not self.initialized:
            await self.start()
        
        message_id = str(uuid.uuid4())
        
        # Enviar chamada de ferramenta
        await self._send_message({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": args
            },
            "id": message_id
        })
        
        # Ler resposta
        response = await self._read_response()
        
        if "error" in response:
            raise Exception(f"Erro MCP: {response['error']}")
        
        return response.get("result", {})
    
    async def _send_message(self, message: dict):
        """Envia mensagem para o servidor MCP"""
        message_str = json.dumps(message) + "\n"
        self.process.stdin.write(message_str)
        self.process.stdin.flush()
        logger.debug(f"Enviado para {self.name}: {message_str.strip()}")
    
    async def _read_response(self) -> dict:
        """Lê resposta do servidor MCP"""
        line = self.process.stdout.readline()
        if not line:
            raise Exception("Sem resposta do servidor MCP")
        
        logger.debug(f"Recebido de {self.name}: {line.strip()}")
        
        try:
            # Tentar encontrar JSON válido na linha
            # Alguns servidores MCP podem incluir headers antes do JSON
            json_start = line.find('{')
            if json_start >= 0:
                return json.loads(line[json_start:])
            return json.loads(line)
        except json.JSONDecodeError:
            logger.error(f"Erro ao decodificar JSON: {line}")
            raise
    
    def stop(self):
        """Para o servidor MCP"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            self.initialized = False

# Gerenciador de Servidores
class ServerManager:
    def __init__(self):
        self.servers: Dict[str, MCPClient] = {}
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Carrega configuração de servidores"""
        config_path = Path("mcp_servers.yaml")
        if config_path.exists():
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
                for server in self.config.get("servers", []):
                    if server.get("enabled", True):
                        self.add_server(
                            name=server["name"],
                            command=server["command"],
                            env_vars=server.get("env_vars", {})
                        )
    
    def add_server(self, name: str, command: str, env_vars: Dict[str, str] = {}):
        """Adiciona um servidor ao gerenciador"""
        self.servers[name] = MCPClient(name, command, env_vars)
        logger.info(f"Servidor {name} adicionado")
    
    async def call_server(self, name: str, tool: str, args: Dict[str, Any]) -> Any:
        """Chama uma ferramenta em um servidor específico"""
        if name not in self.servers:
            raise ValueError(f"Servidor {name} não encontrado")
        
        client = self.servers[name]
        return await client.call_tool(tool, args)
    
    def stop_all(self):
        """Para todos os servidores"""
        for client in self.servers.values():
            client.stop()

# Instância global
manager = ServerManager()

# Endpoints da API
@app.get("/")
async def root():
    return {
        "service": "MCP Gateway",
        "version": "1.0.0",
        "servers": list(manager.servers.keys()),
        "endpoints": {
            "/call": "Chama ferramenta em servidor MCP",
            "/servers": "Lista servidores disponíveis",
            "/health": "Status do gateway"
        }
    }

@app.post("/call")
async def call_tool(request: MCPRequest):
    """Chama uma ferramenta em um servidor MCP"""
    start_time = datetime.now()
    
    try:
        result = await manager.call_server(
            name=request.server,
            tool=request.tool,
            args=request.args
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return MCPResponse(
            server=request.server,
            result=result,
            timestamp=datetime.now().isoformat(),
            duration=duration
        )
    except Exception as e:
        logger.error(f"Erro ao chamar {request.server}.{request.tool}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/servers")
async def list_servers():
    """Lista servidores MCP disponíveis"""
    servers_info = []
    
    for name, client in manager.servers.items():
        servers_info.append({
            "name": name,
            "initialized": client.initialized,
            "running": client.process is not None and client.process.poll() is None
        })
    
    return {"servers": servers_info}

@app.get("/health")
async def health_check():
    """Verifica saúde do gateway"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "servers_count": len(manager.servers),
        "servers": {
            name: client.process is not None and client.process.poll() is None
            for name, client in manager.servers.items()
        }
    }

# Atalhos para servidores específicos
@app.post("/nocodb/{tool}")
async def nocodb_shortcut(tool: str, args: Dict[str, Any] = {}):
    """Atalho para chamar ferramentas do NocoDB"""
    return await call_tool(MCPRequest(
        server="nocodb",
        tool=tool,
        args=args
    ))

# Eventos do ciclo de vida
@app.on_event("shutdown")
async def shutdown_event():
    """Para todos os servidores ao desligar"""
    logger.info("Desligando gateway...")
    manager.stop_all()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)