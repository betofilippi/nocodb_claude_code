"""
Cliente de teste para o MCP Gateway
"""

import requests
import json
from typing import Dict, Any

class MCPGatewayClient:
    def __init__(self, gateway_url: str = "http://localhost:8002"):
        self.gateway_url = gateway_url
    
    def call(self, server: str, tool: str, args: Dict[str, Any] = {}) -> Any:
        """Chama uma ferramenta em um servidor MCP via gateway"""
        response = requests.post(
            f"{self.gateway_url}/call",
            json={
                "server": server,
                "tool": tool,
                "args": args
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Erro: {response.status_code} - {response.text}")
        
        return response.json()
    
    def list_servers(self) -> Dict[str, Any]:
        """Lista servidores disponíveis"""
        response = requests.get(f"{self.gateway_url}/servers")
        return response.json()
    
    def health(self) -> Dict[str, Any]:
        """Verifica saúde do gateway"""
        response = requests.get(f"{self.gateway_url}/health")
        return response.json()
    
    # Atalhos para NocoDB
    def nocodb_list_bases(self) -> Any:
        """Lista bases do NocoDB"""
        return self.call("nocodb", "list_bases")
    
    def nocodb_list_tables(self, base_id: str) -> Any:
        """Lista tabelas de uma base"""
        return self.call("nocodb", "list_tables", {"base_id": base_id})
    
    def nocodb_create_record(self, table_id: str, record_data: Dict[str, Any]) -> Any:
        """Cria registro no NocoDB"""
        return self.call("nocodb", "create_record", {
            "table_id": table_id,
            "record_data": record_data
        })

# Exemplos de uso
if __name__ == "__main__":
    # Criar cliente
    client = MCPGatewayClient()
    
    print("=== Testando MCP Gateway ===\n")
    
    # 1. Verificar saúde
    print("1. Verificando saúde do gateway:")
    health = client.health()
    print(json.dumps(health, indent=2))
    
    # 2. Listar servidores
    print("\n2. Servidores disponíveis:")
    servers = client.list_servers()
    print(json.dumps(servers, indent=2))
    
    # 3. Testar NocoDB
    print("\n3. Testando NocoDB:")
    
    try:
        # Listar bases
        print("\n   a) Listando bases:")
        bases = client.nocodb_list_bases()
        print(json.dumps(bases, indent=2))
        
        # Se houver bases, listar tabelas da primeira
        if bases.get("result", {}).get("list"):
            base_id = bases["result"]["list"][0]["id"]
            print(f"\n   b) Listando tabelas da base {base_id}:")
            tables = client.nocodb_list_tables(base_id)
            print(json.dumps(tables, indent=2))
        
    except Exception as e:
        print(f"Erro ao testar NocoDB: {e}")
    
    # 4. Exemplo genérico
    print("\n4. Chamada genérica:")
    try:
        result = client.call(
            server="nocodb",
            tool="list_bases",
            args={}
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n=== Teste concluído ===")

# Exemplo de integração com agentes
class AgentWithMCPGateway:
    def __init__(self, agent_name: str = "my_agent"):
        self.agent_name = agent_name
        self.mcp = MCPGatewayClient()
    
    async def process_request(self, user_input: str) -> str:
        """Processa requisição do usuário usando MCP"""
        
        # Exemplo: interpretar comando do usuário
        if "listar bases" in user_input.lower():
            result = self.mcp.nocodb_list_bases()
            bases = result["result"]["list"]
            return f"Encontrei {len(bases)} bases: " + ", ".join(b["title"] for b in bases)
        
        elif "criar registro" in user_input.lower():
            # Extrair dados do comando...
            result = self.mcp.nocodb_create_record(
                table_id="tbl_example",
                record_data={"name": "Teste", "value": 123}
            )
            return f"Registro criado com sucesso: {result}"
        
        return "Comando não reconhecido"