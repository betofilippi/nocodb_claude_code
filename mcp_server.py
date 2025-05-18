#!/usr/bin/env python3
"""NocoDB MCP Server - Model Context Protocol server for NocoDB integration"""

import json
import sys
import requests
from typing import Any, Dict

# NocoDB configuration
BASE_URL = "https://planilha.plataforma.app/api/v1/db"
API_KEY = "6PXQIre9nyqukms7OsbUNMPYLsptIVLBgBHe30Jb"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

class NocoDBMCPServer:
    def __init__(self):
        self.handlers = {
            "initialize": self.handle_initialize,
            "tools/list": self.handle_tools_list,
            "tools/call": self.handle_tools_call
        }

    def handle_initialize(self, params):
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "nocodb-mcp-server",
                "version": "1.0.0"
            }
        }

    def handle_tools_list(self, params):
        return {
            "tools": [
                {
                    "name": "get_projects",
                    "description": "Get list of NocoDB projects",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "get_tables",
                    "description": "Get list of tables in a project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project ID"
                            }
                        },
                        "required": ["project_id"]
                    }
                },
                {
                    "name": "get_records",
                    "description": "Get records from a table",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project ID"
                            },
                            "table_id": {
                                "type": "string", 
                                "description": "Table ID"
                            }
                        },
                        "required": ["project_id", "table_id"]
                    }
                }
            ]
        }

    def handle_tools_call(self, params):
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "get_projects":
            return self._get_projects()
        elif tool_name == "get_tables":
            return self._get_tables(arguments.get("project_id"))
        elif tool_name == "get_records":
            return self._get_records(
                arguments.get("project_id"),
                arguments.get("table_id")
            )
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _get_projects(self):
        try:
            response = requests.get(f"{BASE_URL}/meta/projects", headers=HEADERS)
            if response.status_code == 200:
                return {"content": [{"type": "text", "text": json.dumps(response.json())}]}
            else:
                return {"error": f"Failed to get projects: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def _get_tables(self, project_id):
        try:
            response = requests.get(f"{BASE_URL}/meta/projects/{project_id}/tables", headers=HEADERS)
            if response.status_code == 200:
                return {"content": [{"type": "text", "text": json.dumps(response.json())}]}
            else:
                return {"error": f"Failed to get tables: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def _get_records(self, project_id, table_id):
        try:
            response = requests.get(f"{BASE_URL}/data/{project_id}/{table_id}", headers=HEADERS)
            if response.status_code == 200:
                return {"content": [{"type": "text", "text": json.dumps(response.json())}]}
            else:
                return {"error": f"Failed to get records: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

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
                    "message": f"Method not found: {method}"
                }
            }

    def run(self):
        for line in sys.stdin:
            try:
                message = json.loads(line)
                response = self.process_message(message)
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()

if __name__ == "__main__":
    server = NocoDBMCPServer()
    server.run()