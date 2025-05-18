#!/usr/bin/env python3
"""
NocoDB MCP Server - Servidor completo para integração com NocoDB
Inclui todas as principais funções da API
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
NOCODB_API_KEY = os.getenv("NOCODB_API_KEY", "")

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
                "version": "3.0.0",
                "description": "Servidor MCP completo para integração com todas as funções do NocoDB"
            }
        }

    def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "tools": [
                # Informações do sistema
                {
                    "name": "get_info",
                    "description": "Obter informações sobre o servidor NocoDB",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                
                # Gerenciamento de Bases
                {
                    "name": "list_bases",
                    "description": "Listar todas as bases no NocoDB",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "get_base",
                    "description": "Obter detalhes de uma base específica",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "base_id": {
                                "type": "string",
                                "description": "ID da base"
                            }
                        },
                        "required": ["base_id"]
                    }
                },
                {
                    "name": "create_base",
                    "description": "Criar uma nova base",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Nome da base"
                            },
                            "description": {
                                "type": "string",
                                "description": "Descrição da base"
                            }
                        },
                        "required": ["title"]
                    }
                },
                {
                    "name": "update_base",
                    "description": "Atualizar uma base existente",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "base_id": {
                                "type": "string",
                                "description": "ID da base"
                            },
                            "title": {
                                "type": "string",
                                "description": "Novo nome da base"
                            },
                            "description": {
                                "type": "string",
                                "description": "Nova descrição da base"
                            }
                        },
                        "required": ["base_id"]
                    }
                },
                {
                    "name": "delete_base",
                    "description": "Deletar uma base",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "base_id": {
                                "type": "string",
                                "description": "ID da base"
                            }
                        },
                        "required": ["base_id"]
                    }
                },
                
                # Gerenciamento de Tabelas
                {
                    "name": "list_tables",
                    "description": "Listar tabelas de uma base",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "base_id": {
                                "type": "string",
                                "description": "ID da base"
                            }
                        },
                        "required": ["base_id"]
                    }
                },
                {
                    "name": "get_table",
                    "description": "Obter detalhes de uma tabela",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            }
                        },
                        "required": ["table_id"]
                    }
                },
                {
                    "name": "create_table",
                    "description": "Criar uma nova tabela",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "base_id": {
                                "type": "string",
                                "description": "ID da base"
                            },
                            "title": {
                                "type": "string",
                                "description": "Nome da tabela"
                            },
                            "columns": {
                                "type": "array",
                                "description": "Lista de colunas da tabela"
                            }
                        },
                        "required": ["base_id", "title"]
                    }
                },
                {
                    "name": "update_table",
                    "description": "Atualizar uma tabela",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "title": {
                                "type": "string",
                                "description": "Novo nome da tabela"
                            }
                        },
                        "required": ["table_id"]
                    }
                },
                {
                    "name": "delete_table",
                    "description": "Deletar uma tabela",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            }
                        },
                        "required": ["table_id"]
                    }
                },
                
                # Gerenciamento de Colunas
                {
                    "name": "list_columns",
                    "description": "Listar colunas de uma tabela",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            }
                        },
                        "required": ["table_id"]
                    }
                },
                {
                    "name": "create_column",
                    "description": "Criar uma nova coluna",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "title": {
                                "type": "string",
                                "description": "Nome da coluna"
                            },
                            "column_type": {
                                "type": "string",
                                "description": "Tipo da coluna (SingleLineText, LongText, Number, etc.)"
                            }
                        },
                        "required": ["table_id", "title", "column_type"]
                    }
                },
                {
                    "name": "update_column",
                    "description": "Atualizar uma coluna",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "column_id": {
                                "type": "string",
                                "description": "ID da coluna"
                            },
                            "title": {
                                "type": "string",
                                "description": "Novo nome da coluna"
                            }
                        },
                        "required": ["column_id"]
                    }
                },
                {
                    "name": "delete_column",
                    "description": "Deletar uma coluna",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "column_id": {
                                "type": "string",
                                "description": "ID da coluna"
                            }
                        },
                        "required": ["column_id"]
                    }
                },
                
                # Gerenciamento de Registros
                {
                    "name": "list_records",
                    "description": "Listar registros de uma tabela",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
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
                            },
                            "where": {
                                "type": "string",
                                "description": "Filtro WHERE",
                                "default": ""
                            },
                            "sort": {
                                "type": "string",
                                "description": "Ordenação dos resultados"
                            }
                        },
                        "required": ["table_id"]
                    }
                },
                {
                    "name": "get_record",
                    "description": "Obter um registro específico",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "record_id": {
                                "type": "string",
                                "description": "ID do registro"
                            }
                        },
                        "required": ["table_id", "record_id"]
                    }
                },
                {
                    "name": "create_record",
                    "description": "Criar um novo registro",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "data": {
                                "type": "object",
                                "description": "Dados do registro a criar"
                            }
                        },
                        "required": ["table_id", "data"]
                    }
                },
                {
                    "name": "update_record",
                    "description": "Atualizar um registro existente",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
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
                        "required": ["table_id", "record_id", "data"]
                    }
                },
                {
                    "name": "delete_record",
                    "description": "Deletar um registro",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "record_id": {
                                "type": "string",
                                "description": "ID do registro"
                            }
                        },
                        "required": ["table_id", "record_id"]
                    }
                },
                {
                    "name": "bulk_create_records",
                    "description": "Criar múltiplos registros de uma vez",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "records": {
                                "type": "array",
                                "description": "Lista de registros para criar"
                            }
                        },
                        "required": ["table_id", "records"]
                    }
                },
                {
                    "name": "bulk_update_records",
                    "description": "Atualizar múltiplos registros de uma vez",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "records": {
                                "type": "array",
                                "description": "Lista de registros para atualizar"
                            }
                        },
                        "required": ["table_id", "records"]
                    }
                },
                {
                    "name": "bulk_delete_records",
                    "description": "Deletar múltiplos registros de uma vez",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "record_ids": {
                                "type": "array",
                                "description": "Lista de IDs dos registros para deletar"
                            }
                        },
                        "required": ["table_id", "record_ids"]
                    }
                },
                
                # Gerenciamento de Views
                {
                    "name": "list_views",
                    "description": "Listar views de uma tabela",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            }
                        },
                        "required": ["table_id"]
                    }
                },
                {
                    "name": "create_view",
                    "description": "Criar uma nova view",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "title": {
                                "type": "string",
                                "description": "Nome da view"
                            },
                            "type": {
                                "type": "string",
                                "description": "Tipo da view (grid, gallery, form, etc.)"
                            }
                        },
                        "required": ["table_id", "title", "type"]
                    }
                },
                {
                    "name": "update_view",
                    "description": "Atualizar uma view",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "view_id": {
                                "type": "string",
                                "description": "ID da view"
                            },
                            "title": {
                                "type": "string",
                                "description": "Novo nome da view"
                            }
                        },
                        "required": ["view_id"]
                    }
                },
                {
                    "name": "delete_view",
                    "description": "Deletar uma view",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "view_id": {
                                "type": "string",
                                "description": "ID da view"
                            }
                        },
                        "required": ["view_id"]
                    }
                },
                
                # Operações de Filtro
                {
                    "name": "create_filter",
                    "description": "Criar um filtro para uma view",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "view_id": {
                                "type": "string",
                                "description": "ID da view"
                            },
                            "field": {
                                "type": "string",
                                "description": "Campo para filtrar"
                            },
                            "operator": {
                                "type": "string",
                                "description": "Operador do filtro"
                            },
                            "value": {
                                "type": "string",
                                "description": "Valor do filtro"
                            }
                        },
                        "required": ["view_id", "field", "operator", "value"]
                    }
                },
                
                # Operações de Ordenação
                {
                    "name": "create_sort",
                    "description": "Criar ordenação para uma view",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "view_id": {
                                "type": "string",
                                "description": "ID da view"
                            },
                            "field": {
                                "type": "string",
                                "description": "Campo para ordenar"
                            },
                            "direction": {
                                "type": "string",
                                "description": "Direção da ordenação (asc ou desc)"
                            }
                        },
                        "required": ["view_id", "field", "direction"]
                    }
                },
                
                # Webhooks
                {
                    "name": "list_webhooks",
                    "description": "Listar webhooks de uma tabela",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            }
                        },
                        "required": ["table_id"]
                    }
                },
                {
                    "name": "create_webhook",
                    "description": "Criar um webhook",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "title": {
                                "type": "string",
                                "description": "Nome do webhook"
                            },
                            "event": {
                                "type": "string",
                                "description": "Evento (insert, update, delete)"
                            },
                            "url": {
                                "type": "string",
                                "description": "URL do webhook"
                            }
                        },
                        "required": ["table_id", "title", "event", "url"]
                    }
                },
                
                # Compartilhamento
                {
                    "name": "share_view",
                    "description": "Compartilhar uma view publicamente",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "view_id": {
                                "type": "string",
                                "description": "ID da view"
                            },
                            "password": {
                                "type": "string",
                                "description": "Senha para proteger a view (opcional)"
                            }
                        },
                        "required": ["view_id"]
                    }
                },
                
                # Pesquisa Global
                {
                    "name": "global_search",
                    "description": "Pesquisar em todas as tabelas",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "base_id": {
                                "type": "string",
                                "description": "ID da base"
                            },
                            "query": {
                                "type": "string",
                                "description": "Termo de pesquisa"
                            }
                        },
                        "required": ["base_id", "query"]
                    }
                },
                
                # Comentários
                {
                    "name": "add_comment",
                    "description": "Adicionar comentário a um registro",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "record_id": {
                                "type": "string",
                                "description": "ID do registro"
                            },
                            "comment": {
                                "type": "string",
                                "description": "Texto do comentário"
                            }
                        },
                        "required": ["table_id", "record_id", "comment"]
                    }
                },
                
                # Arquivo e Upload
                {
                    "name": "upload_file",
                    "description": "Fazer upload de arquivo",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_id": {
                                "type": "string",
                                "description": "ID da tabela"
                            },
                            "column_id": {
                                "type": "string",
                                "description": "ID da coluna de arquivo"
                            },
                            "file_url": {
                                "type": "string",
                                "description": "URL do arquivo para upload"
                            }
                        },
                        "required": ["table_id", "column_id", "file_url"]
                    }
                }
            ]
        }

    def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        tool_handlers = {
            # Informações
            "get_info": self._get_info,
            
            # Bases
            "list_bases": self._list_bases,
            "get_base": self._get_base,
            "create_base": self._create_base,
            "update_base": self._update_base,
            "delete_base": self._delete_base,
            
            # Tabelas
            "list_tables": self._list_tables,
            "get_table": self._get_table,
            "create_table": self._create_table,
            "update_table": self._update_table,
            "delete_table": self._delete_table,
            
            # Colunas
            "list_columns": self._list_columns,
            "create_column": self._create_column,
            "update_column": self._update_column,
            "delete_column": self._delete_column,
            
            # Registros
            "list_records": self._list_records,
            "get_record": self._get_record,
            "create_record": self._create_record,
            "update_record": self._update_record,
            "delete_record": self._delete_record,
            "bulk_create_records": self._bulk_create_records,
            "bulk_update_records": self._bulk_update_records,
            "bulk_delete_records": self._bulk_delete_records,
            
            # Views
            "list_views": self._list_views,
            "create_view": self._create_view,
            "update_view": self._update_view,
            "delete_view": self._delete_view,
            
            # Filtros e Ordenação
            "create_filter": self._create_filter,
            "create_sort": self._create_sort,
            
            # Webhooks
            "list_webhooks": self._list_webhooks,
            "create_webhook": self._create_webhook,
            
            # Compartilhamento
            "share_view": self._share_view,
            
            # Pesquisa
            "global_search": self._global_search,
            
            # Comentários
            "add_comment": self._add_comment,
            
            # Upload
            "upload_file": self._upload_file
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
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data)
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

    # Implementação dos métodos
    def _get_info(self) -> Dict[str, Any]:
        return self._make_request("GET", "/meta/info")

    # Bases
    def _list_bases(self) -> Dict[str, Any]:
        return self._make_request("GET", "/meta/bases")

    def _get_base(self, base_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/meta/bases/{base_id}")

    def _create_base(self, title: str, description: str = None) -> Dict[str, Any]:
        data = {"title": title}
        if description:
            data["description"] = description
        return self._make_request("POST", "/meta/bases", data)

    def _update_base(self, base_id: str, title: str = None, description: str = None) -> Dict[str, Any]:
        data = {}
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        return self._make_request("PATCH", f"/meta/bases/{base_id}", data)

    def _delete_base(self, base_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/meta/bases/{base_id}")

    # Tabelas
    def _list_tables(self, base_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/meta/bases/{base_id}/tables")

    def _get_table(self, table_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/meta/tables/{table_id}")

    def _create_table(self, base_id: str, title: str, columns: List[Dict] = None) -> Dict[str, Any]:
        data = {"title": title}
        if columns:
            data["columns"] = columns
        return self._make_request("POST", f"/meta/bases/{base_id}/tables", data)

    def _update_table(self, table_id: str, title: str) -> Dict[str, Any]:
        return self._make_request("PATCH", f"/meta/tables/{table_id}", {"title": title})

    def _delete_table(self, table_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/meta/tables/{table_id}")

    # Colunas
    def _list_columns(self, table_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/meta/tables/{table_id}/columns")

    def _create_column(self, table_id: str, title: str, column_type: str) -> Dict[str, Any]:
        data = {
            "title": title,
            "uidt": column_type  # UI Data Type
        }
        return self._make_request("POST", f"/meta/tables/{table_id}/columns", data)

    def _update_column(self, column_id: str, title: str) -> Dict[str, Any]:
        return self._make_request("PATCH", f"/meta/columns/{column_id}", {"title": title})

    def _delete_column(self, column_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/meta/columns/{column_id}")

    # Registros
    def _list_records(self, table_id: str, limit: int = 50, offset: int = 0, where: str = "", sort: str = None) -> Dict[str, Any]:
        params = {
            "limit": limit,
            "offset": offset
        }
        if where:
            params["where"] = where
        if sort:
            params["sort"] = sort
        return self._make_request("GET", f"/tables/{table_id}/records", params=params)

    def _get_record(self, table_id: str, record_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/tables/{table_id}/records/{record_id}")

    def _create_record(self, table_id: str, data: Dict) -> Dict[str, Any]:
        return self._make_request("POST", f"/tables/{table_id}/records", data)

    def _update_record(self, table_id: str, record_id: str, data: Dict) -> Dict[str, Any]:
        return self._make_request("PATCH", f"/tables/{table_id}/records/{record_id}", data)

    def _delete_record(self, table_id: str, record_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/tables/{table_id}/records/{record_id}")

    def _bulk_create_records(self, table_id: str, records: List[Dict]) -> Dict[str, Any]:
        return self._make_request("POST", f"/tables/{table_id}/records/bulk", records)

    def _bulk_update_records(self, table_id: str, records: List[Dict]) -> Dict[str, Any]:
        return self._make_request("PATCH", f"/tables/{table_id}/records/bulk", records)

    def _bulk_delete_records(self, table_id: str, record_ids: List[str]) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/tables/{table_id}/records/bulk", {"ids": record_ids})

    # Views
    def _list_views(self, table_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/meta/tables/{table_id}/views")

    def _create_view(self, table_id: str, title: str, type: str) -> Dict[str, Any]:
        data = {
            "title": title,
            "type": type
        }
        return self._make_request("POST", f"/meta/tables/{table_id}/views", data)

    def _update_view(self, view_id: str, title: str) -> Dict[str, Any]:
        return self._make_request("PATCH", f"/meta/views/{view_id}", {"title": title})

    def _delete_view(self, view_id: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/meta/views/{view_id}")

    # Filtros
    def _create_filter(self, view_id: str, field: str, operator: str, value: str) -> Dict[str, Any]:
        data = {
            "fk_column_id": field,
            "comparison_op": operator,
            "value": value
        }
        return self._make_request("POST", f"/meta/views/{view_id}/filters", data)

    # Ordenação
    def _create_sort(self, view_id: str, field: str, direction: str) -> Dict[str, Any]:
        data = {
            "fk_column_id": field,
            "direction": direction
        }
        return self._make_request("POST", f"/meta/views/{view_id}/sorts", data)

    # Webhooks
    def _list_webhooks(self, table_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/meta/tables/{table_id}/hooks")

    def _create_webhook(self, table_id: str, title: str, event: str, url: str) -> Dict[str, Any]:
        data = {
            "title": title,
            "event": event,
            "notification": {
                "type": "URL",
                "payload": {
                    "method": "POST",
                    "url": url
                }
            }
        }
        return self._make_request("POST", f"/meta/tables/{table_id}/hooks", data)

    # Compartilhamento
    def _share_view(self, view_id: str, password: str = None) -> Dict[str, Any]:
        data = {}
        if password:
            data["password"] = password
        return self._make_request("POST", f"/meta/views/{view_id}/share", data)

    # Pesquisa Global
    def _global_search(self, base_id: str, query: str) -> Dict[str, Any]:
        params = {"query": query}
        return self._make_request("GET", f"/meta/bases/{base_id}/search", params=params)

    # Comentários
    def _add_comment(self, table_id: str, record_id: str, comment: str) -> Dict[str, Any]:
        data = {"description": comment}
        return self._make_request("POST", f"/tables/{table_id}/records/{record_id}/comments", data)

    # Upload
    def _upload_file(self, table_id: str, column_id: str, file_url: str) -> Dict[str, Any]:
        data = {
            "url": file_url,
            "fk_column_id": column_id
        }
        return self._make_request("POST", f"/tables/{table_id}/files", data)

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
        logger.info("Servidor MCP NocoDB completo iniciado")
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