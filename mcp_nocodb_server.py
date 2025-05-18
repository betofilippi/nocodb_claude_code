#!/usr/bin/env python3
"""
NocoDB MCP Server - Servidor completo para integração com NocoDB
"""

import json
import sys
import logging
import os
import requests
from typing import Any, Dict, List, Optional

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração do NocoDB
NOCODB_BASE_URL = os.getenv("NOCODB_BASE_URL", "https://nocodb.plataforma.app/api/v2")
NOCODB_API_KEY = os.getenv("NOCODB_API_KEY", "FjBfW7RYV76huT4cYd78P642GqDXwXn4c05dBzoE")

class NocoDBMCPServer:
    def __init__(self):
        self.base_url = NOCODB_BASE_URL
        self.api_key = NOCODB_API_KEY
        self.headers = {
            "xc-token": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Mapeamento de métodos
        self.handlers = {
            "initialize": self.handle_initialize,
            "tools/list": self.handle_tools_list,
            "tools/call": self.handle_tools_call,
            "resources/list": self.handle_resources_list,
            "resources/read": self.handle_resources_read
        }

    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {
                    "read": True,
                    "write": False
                }
            },
            "serverInfo": {
                "name": "nocodb-mcp-server",
                "version": "2.0.0",
                "description": "Servidor MCP completo para integração com NocoDB"
            }
        }

    def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "tools": [
                {
                    "name": "get_info",
                    "description": "Obter informações sobre o servidor NocoDB",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "list_bases",
                    "description": "Listar todas as bases no NocoDB",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "get_project",
                    "description": "Obter detalhes de um projeto específico",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "ID do projeto"
                            }
                        },
                        "required": ["project_id"]
                    }
                },
                {
                    "name": "list_tables",
                    "description": "Listar tabelas de um projeto",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "ID do projeto"
                            }
                        },
                        "required": ["project_id"]
                    }
                },
                {
                    "name": "get_table_schema",
                    "description": "Obter esquema de uma tabela",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "ID do projeto"
                            },
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            }
                        },
                        "required": ["project_id", "table_id"]
                    }
                },
                {
                    "name": "list_records",
                    "description": "Listar registros de uma tabela",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "ID do projeto"
                            },
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Número máximo de registros",
                                "default": 50
                            },
                            "offset": {
                                "type": "integer",
                                "description": "Offset para paginação",
                                "default": 0
                            }
                        },
                        "required": ["project_id", "table_id"]
                    }
                },
                {
                    "name": "get_record",
                    "description": "Obter um registro específico",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "ID do projeto"
                            },
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "record_id": {
                                "type": "string",
                                "description": "ID do registro"
                            }
                        },
                        "required": ["project_id", "table_id", "record_id"]
                    }
                },
                {
                    "name": "create_record",
                    "description": "Criar um novo registro",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "ID do projeto"
                            },
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "data": {
                                "type": "object",
                                "description": "Dados do registro a criar"
                            }
                        },
                        "required": ["project_id", "table_id", "data"]
                    }
                },
                {
                    "name": "update_record",
                    "description": "Atualizar um registro existente",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "ID do projeto"
                            },
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "record_id": {
                                "type": "string",
                                "description": "ID do registro"
                            },
                            "data": {
                                "type": "object",
                                "description": "Dados para atualizar"
                            }
                        },
                        "required": ["project_id", "table_id", "record_id", "data"]
                    }
                },
                {
                    "name": "delete_record",
                    "description": "Deletar um registro",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "ID do projeto"
                            },
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "record_id": {
                                "type": "string",
                                "description": "ID do registro"
                            }
                        },
                        "required": ["project_id", "table_id", "record_id"]
                    }
                }
            ]
        }

    def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        tool_handlers = {
            "get_info": self._get_info,
            "list_bases": self._list_bases,
            "get_project": self._get_project,
            "list_tables": self._list_tables,
            "get_table_schema": self._get_table_schema,
            "list_records": self._list_records,
            "get_record": self._get_record,
            "create_record": self._create_record,
            "update_record": self._update_record,
            "delete_record": self._delete_record
        }

        handler = tool_handlers.get(tool_name)
        if handler:
            return handler(**arguments)
        else:
            return {"error": f"Ferramenta desconhecida: {tool_name}"}

    def handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"resources": []}

    def handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"error": "Recursos não implementados"}

    # Métodos de API do NocoDB
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                return {"error": f"Método HTTP não suportado: {method}"}

            if response.status_code in [200, 201, 204]:
                if response.content:
                    return {"content": [{"type": "text", "text": json.dumps(response.json())}]}
                else:
                    return {"content": [{"type": "text", "text": "Operação realizada com sucesso"}]}
            else:
                return {"error": f"Erro na requisição: {response.status_code} - {response.text}"}
        except Exception as e:
            return {"error": str(e)}

    def _get_info(self) -> Dict[str, Any]:
        return self._make_request("GET", "/meta/info")

    def _list_bases(self) -> Dict[str, Any]:
        return self._make_request("GET", "/meta/bases")

    def _get_project(self, project_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/meta/bases/{project_id}")

    def _list_tables(self, project_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/meta/bases/{project_id}/tables")

    def _get_table_schema(self, project_id: str, table_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/meta/tables/{table_id}")

    def _list_records(self, project_id: str, table_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        endpoint = f"/tables/{table_id}/records?limit={limit}&offset={offset}"
        return self._make_request("GET", endpoint)

    def _get_record(self, project_id: str, table_id: str, record_id: str) -> Dict[str, Any]:
        endpoint = f"/tables/{table_id}/records/{record_id}"
        return self._make_request("GET", endpoint)

    def _create_record(self, project_id: str, table_id: str, data: Dict) -> Dict[str, Any]:
        endpoint = f"/tables/{table_id}/records"
        return self._make_request("POST", endpoint, data)

    def _update_record(self, project_id: str, table_id: str, record_id: str, data: Dict) -> Dict[str, Any]:
        endpoint = f"/tables/{table_id}/records/{record_id}"
        return self._make_request("PUT", endpoint, data)

    def _delete_record(self, project_id: str, table_id: str, record_id: str) -> Dict[str, Any]:
        endpoint = f"/tables/{table_id}/records/{record_id}"
        return self._make_request("DELETE", endpoint)

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        method = message.get("method")
        params = message.get("params", {})
        id = message.get("id")

        if method in self.handlers:
            result = self.handlers[method](params)
            return {
                "jsonrpc": "2.0",
                "id": id,
                "result": result
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": id,
                "error": {
                    "code": -32601,
                    "message": f"Método não encontrado: {method}"
                }
            }

    def run(self):
        logger.info("Servidor MCP NocoDB iniciado")
        for line in sys.stdin:
            try:
                message = json.loads(line.strip())
                response = self.process_message(message)
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": f"Erro de parse: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                logger.error(f"Erro inesperado: {str(e)}")

if __name__ == "__main__":
    server = NocoDBMCPServer()
    server.run()