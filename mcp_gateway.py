"""
MCP Gateway Universal - Gerencia múltiplos MCP servers e expõe via API REST
"""

import json
import asyncio
import subprocess
import sys
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import logging
from datetime import datetime
import yaml
import os
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Gateway Universal", version="1.0.0")

# Modelos
class MCPRequest(BaseModel):
    server: str  # Nome do servidor MCP
    method: str  # Método a chamar
    params: Dict[str, Any] = {}
    
class MCPResponse(BaseModel):
    server: str
    result: Any
    timestamp: str
    duration: float
    
class ServerConfig(BaseModel):
    name: str
    command: str  # Comando para executar o servidor
    description: str
    enabled: bool = True
    env_vars: Dict[str, str] = {}
    
class RegisterServerRequest(BaseModel):
    name: str
    command: str
    description: str
    env_vars: Dict[str, str] = {}

# Gerenciador de Servidores MCP
class MCPServerManager:
    def __init__(self):
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.load_config()
    
    def load_config(self):
        """Carrega configuração de servidores do arquivo YAML"""
        config_path = Path("mcp_servers.yaml")
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                for server in config.get("servers", []):
                    self.register_server(
                        name=server["name"],
                        command=server["command"],
                        description=server.get("description", ""),
                        env_vars=server.get("env_vars", {})
                    )
    
    def save_config(self):
        """Salva configuração atual em arquivo YAML"""
        config = {
            "servers": [
                {
                    "name": name,
                    "command": info["command"],
                    "description": info["description"],
                    "env_vars": info["env_vars"],
                    "enabled": info["enabled"]
                }
                for name, info in self.servers.items()
            ]
        }
        with open("mcp_servers.yaml", "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def register_server(self, name: str, command: str, description: str = "", env_vars: Dict[str, str] = {}):
        """Registra um novo servidor MCP"""
        self.servers[name] = {
            "command": command,
            "description": description,
            "env_vars": env_vars,
            "enabled": True,
            "status": "registered"
        }
        logger.info(f"Servidor MCP registrado: {name}")
        self.save_config()
    
    def start_server(self, name: str):
        """Inicia um servidor MCP"""
        if name not in self.servers:
            raise ValueError(f"Servidor {name} não registrado")
        
        if name in self.processes and self.processes[name].poll() is None:
            logger.warning(f"Servidor {name} já está rodando")
            return
        
        server_info = self.servers[name]
        env = os.environ.copy()
        env.update(server_info["env_vars"])
        
        try:
            process = subprocess.Popen(
                server_info["command"].split(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                universal_newlines=True,
                bufsize=0
            )
            self.processes[name] = process
            self.servers[name]["status"] = "running"
            logger.info(f"Servidor {name} iniciado com PID {process.pid}")
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor {name}: {e}")
            self.servers[name]["status"] = "error"
            raise
    
    def stop_server(self, name: str):
        """Para um servidor MCP"""
        if name in self.processes:
            process = self.processes[name]
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"Servidor {name} parado")
            del self.processes[name]
            self.servers[name]["status"] = "stopped"
    
    async def call_server(self, name: str, method: str, params: Dict[str, Any]) -> Any:
        """Chama um método em um servidor MCP específico"""
        if name not in self.servers:
            raise ValueError(f"Servidor {name} não encontrado")
        
        if name not in self.processes or self.processes[name].poll() is not None:
            # Servidor não está rodando, tenta iniciar
            self.start_server(name)
            await asyncio.sleep(1)  # Aguarda servidor inicializar
        
        process = self.processes[name]
        
        # Criar mensagem JSON-RPC
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": f"{name}_{method}_{datetime.now().timestamp()}"
        }
        
        try:
            # Enviar mensagem para o servidor
            message_str = json.dumps(message) + "\n"
            process.stdin.write(message_str)
            process.stdin.flush()
            
            # Ler resposta
            response_str = process.stdout.readline()
            if not response_str:
                raise Exception("Sem resposta do servidor")
            
            response = json.loads(response_str)
            
            if "error" in response:
                raise Exception(response["error"])
            
            return response.get("result")
            
        except Exception as e:
            logger.error(f"Erro ao chamar {name}.{method}: {e}")
            raise

# Instância global do gerenciador
manager = MCPServerManager()

# Endpoints da API
@app.get("/")
async def root():
    return {
        "service": "MCP Gateway Universal",
        "version": "1.0.0",
        "endpoints": {
            "/servers": "Lista servidores MCP registrados",
            "/servers/register": "Registra novo servidor MCP",
            "/servers/{name}/start": "Inicia servidor específico",
            "/servers/{name}/stop": "Para servidor específico",
            "/servers/{name}/status": "Status do servidor",
            "/call": "Chama método em servidor MCP",
            "/health": "Status do gateway"
        }
    }

@app.get("/servers")
async def list_servers():
    """Lista todos os servidores MCP registrados"""
    return {
        "servers": [
            {
                "name": name,
                "description": info["description"],
                "status": info["status"],
                "enabled": info["enabled"]
            }
            for name, info in manager.servers.items()
        ]
    }

@app.post("/servers/register")
async def register_server(request: RegisterServerRequest):
    """Registra um novo servidor MCP"""
    try:
        manager.register_server(
            name=request.name,
            command=request.command,
            description=request.description,
            env_vars=request.env_vars
        )
        return {"message": f"Servidor {request.name} registrado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/servers/{name}/start")
async def start_server(name: str):
    """Inicia um servidor MCP específico"""
    try:
        manager.start_server(name)
        return {"message": f"Servidor {name} iniciado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/servers/{name}/stop")
async def stop_server(name: str):
    """Para um servidor MCP específico"""
    try:
        manager.stop_server(name)
        return {"message": f"Servidor {name} parado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/servers/{name}/status")
async def server_status(name: str):
    """Retorna status de um servidor MCP"""
    if name not in manager.servers:
        raise HTTPException(status_code=404, detail=f"Servidor {name} não encontrado")
    
    server_info = manager.servers[name]
    is_running = name in manager.processes and manager.processes[name].poll() is None
    
    return {
        "name": name,
        "description": server_info["description"],
        "status": "running" if is_running else server_info["status"],
        "enabled": server_info["enabled"],
        "pid": manager.processes[name].pid if is_running else None
    }

@app.post("/call")
async def call_mcp_server(request: MCPRequest):
    """Chama um método em um servidor MCP"""
    start_time = datetime.now()
    
    try:
        result = await manager.call_server(
            name=request.server,
            method=request.method,
            params=request.params
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return MCPResponse(
            server=request.server,
            result=result,
            timestamp=datetime.now().isoformat(),
            duration=duration
        )
    except Exception as e:
        logger.error(f"Erro ao chamar {request.server}.{request.method}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Verifica saúde do gateway e servidores"""
    servers_status = {}
    
    for name in manager.servers:
        is_running = name in manager.processes and manager.processes[name].poll() is None
        servers_status[name] = "running" if is_running else "stopped"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "servers": servers_status,
        "total_servers": len(manager.servers),
        "running_servers": sum(1 for status in servers_status.values() if status == "running")
    }

# Eventos de inicialização/finalização
@app.on_event("startup")
async def startup_event():
    """Inicializa gateway e servidores configurados para auto-start"""
    logger.info("MCP Gateway iniciando...")
    
    # Iniciar servidores marcados como auto-start
    for name, info in manager.servers.items():
        if info.get("auto_start", False):
            try:
                manager.start_server(name)
            except Exception as e:
                logger.error(f"Erro ao auto-iniciar {name}: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Para todos os servidores MCP ao desligar"""
    logger.info("MCP Gateway desligando...")
    
    for name in list(manager.processes.keys()):
        try:
            manager.stop_server(name)
        except Exception as e:
            logger.error(f"Erro ao parar {name}: {e}")

# Endpoints de conveniência para servidores específicos
@app.post("/nocodb/{method}")
async def nocodb_shortcut(method: str, params: Dict[str, Any] = {}):
    """Atalho para chamar métodos do NocoDB"""
    request = MCPRequest(
        server="nocodb",
        method=f"tools/call",
        params={"name": method, "arguments": params}
    )
    return await call_mcp_server(request)

if __name__ == "__main__":
    # Configuração inicial de exemplo
    initial_config = {
        "servers": [
            {
                "name": "nocodb",
                "command": "python /path/to/mcp_nocodb_server_full.py",
                "description": "NocoDB MCP Server",
                "env_vars": {
                    "NOCODB_BASE_URL": "https://nocodb.plataforma.app/api/v2",
                    "NOCODB_API_KEY": "your_token_here"
                }
            }
        ]
    }
    
    # Criar arquivo de configuração se não existir
    if not Path("mcp_servers.yaml").exists():
        with open("mcp_servers.yaml", "w") as f:
            yaml.dump(initial_config, f)
    
    # Iniciar gateway
    uvicorn.run(app, host="0.0.0.0", port=8001)