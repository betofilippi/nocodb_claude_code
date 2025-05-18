"""
Exemplo de implementação do NocoDB tool para OpenAI Assistant
"""

import os
import json
import requests
from openai import OpenAI

# Configuração
NOCODB_API_URL = "https://nocodbclaudecode-production.up.railway.app/execute"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def nocodb_execute(tool: str, args: dict) -> dict:
    """
    Executa operações no NocoDB através do servidor HTTP
    
    Args:
        tool: Nome da operação (list_bases, create_record, etc.)
        args: Argumentos específicos para a operação
    
    Returns:
        dict: Resultado da operação ou erro
    """
    payload = {
        "tool": tool,
        "args": args
    }
    
    try:
        response = requests.post(
            NOCODB_API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro na requisição: {str(e)}"}
    except Exception as e:
        return {"error": f"Erro inesperado: {str(e)}"}

# Definição da função para o Assistant
function_definition = {
    "name": "nocodb_execute",
    "description": "Execute operations on NocoDB database",
    "parameters": {
        "type": "object",
        "properties": {
            "tool": {
                "type": "string",
                "description": "The operation to execute"
            },
            "args": {
                "type": "object",
                "description": "Arguments for the operation"
            }
        },
        "required": ["tool", "args"]
    }
}

# Instruções do sistema
system_instructions = """
Você é um assistente que gerencia dados no NocoDB. Use a função nocodb_execute para:

- Listar e gerenciar bases de dados
- Criar, ler, atualizar e deletar registros
- Gerenciar tabelas e colunas
- Configurar views, filtros e ordenações
- Executar operações em lote
- Realizar buscas

Sempre forneça feedback claro sobre as operações realizadas e trate erros adequadamente.

Exemplos:
- Para listar bases: nocodb_execute("list_bases", {})
- Para criar registro: nocodb_execute("create_record", {"table_id": "id", "record_data": {...}})
- Para buscar registros: nocodb_execute("list_records", {"table_id": "id", "where": "filtro"})
"""

# Exemplo de uso com o Assistant
def create_assistant():
    """Cria um Assistant com a função NocoDB"""
    assistant = client.beta.assistants.create(
        name="NocoDB Manager",
        instructions=system_instructions,
        model="gpt-4-turbo-preview",
        tools=[{
            "type": "function",
            "function": function_definition
        }]
    )
    return assistant

# Handler para processar chamadas de função
def handle_function_call(name: str, arguments: str) -> dict:
    """Processa chamadas de função do Assistant"""
    if name == "nocodb_execute":
        args = json.loads(arguments)
        return nocodb_execute(args["tool"], args["args"])
    else:
        return {"error": f"Função desconhecida: {name}"}

# Exemplo de conversa
def run_conversation(assistant_id: str, user_message: str):
    """Executa uma conversa com o Assistant"""
    
    # Criar thread
    thread = client.beta.threads.create()
    
    # Adicionar mensagem do usuário
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )
    
    # Executar o Assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    
    # Aguardar conclusão
    while run.status not in ["completed", "failed", "cancelled"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        
        # Processar chamadas de função se necessário
        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            
            for tool_call in tool_calls:
                output = handle_function_call(
                    tool_call.function.name,
                    tool_call.function.arguments
                )
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(output)
                })
            
            # Submeter outputs
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
        
        # Aguardar um pouco antes de verificar novamente
        import time
        time.sleep(1)
    
    # Obter mensagens
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    
    # Retornar a última mensagem do Assistant
    for message in messages.data:
        if message.role == "assistant":
            return message.content[0].text.value
    
    return "Nenhuma resposta do Assistant"

# Exemplo de uso
if __name__ == "__main__":
    # Criar Assistant (fazer apenas uma vez)
    # assistant = create_assistant()
    # print(f"Assistant criado: {assistant.id}")
    
    # Usar Assistant existente
    assistant_id = "seu_assistant_id_aqui"
    
    # Exemplos de conversas
    examples = [
        "Liste todas as bases disponíveis no NocoDB",
        "Crie um novo registro na tabela Clientes com nome João Silva",
        "Busque todos os registros ativos na tabela Pedidos",
        "Qual é a estrutura da tabela Produtos?"
    ]
    
    for example in examples:
        print(f"\nUsuário: {example}")
        response = run_conversation(assistant_id, example)
        print(f"Assistant: {response}")