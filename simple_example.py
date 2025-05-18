"""
Exemplo SUPER SIMPLES - NocoDB Assistant
Execute este arquivo no seu computador!
"""

import requests
from openai import OpenAI

# ===== CONFIGURAÇÕES (mude aqui!) =====
OPENAI_API_KEY = "sk-..."  # Sua chave da OpenAI
ASSISTANT_ID = "asst_..."  # ID do seu Assistant (pega no playground)

# Inicializar OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def chamar_nocodb(tool, args):
    """Esta função chama o servidor no Railway"""
    url = "https://nocodbclaudecode-production.up.railway.app/execute"
    
    response = requests.post(url, json={
        "tool": tool,
        "args": args
    })
    
    return response.json()

def conversar(mensagem):
    """Conversa com o Assistant"""
    
    # 1. Criar uma conversa
    thread = client.beta.threads.create()
    
    # 2. Enviar mensagem
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=mensagem
    )
    
    # 3. Rodar o Assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )
    
    # 4. Esperar resposta
    import time
    while run.status != "completed":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        
        # 5. Se o Assistant quer chamar uma função
        if run.status == "requires_action":
            print("Assistant quer chamar o NocoDB...")
            
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            outputs = []
            
            for tool_call in tool_calls:
                # Pegar os argumentos
                import json
                args = json.loads(tool_call.function.arguments)
                
                # CHAMAR O NOCODB!
                print(f"Chamando: {args['tool']}")
                result = chamar_nocodb(args["tool"], args["args"])
                
                outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(result)
                })
            
            # Enviar resultado de volta
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=outputs
            )
    
    # 6. Pegar resposta final
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

# ===== USAR O ASSISTANT =====
if __name__ == "__main__":
    print("🤖 NocoDB Assistant")
    print("=" * 30)
    print("Digite 'sair' para terminar")
    print()
    
    while True:
        # Pedir input do usuário
        user_message = input("Você: ")
        
        if user_message.lower() == 'sair':
            print("Tchau! 👋")
            break
        
        # Conversar com o Assistant
        print("\nAssistant: ", end="")
        try:
            response = conversar(user_message)
            print(response)
        except Exception as e:
            print(f"Erro: {e}")
        
        print()  # Linha em branco

"""
COMO USAR:

1. Instale as dependências:
   pip install openai requests

2. Configure:
   - Coloque sua API key da OpenAI
   - Coloque o ID do seu Assistant

3. Execute:
   python simple_example.py

4. Converse:
   Você: Liste as bases do NocoDB
   Assistant: Vou listar as bases disponíveis...
   
O código vai:
- Receber sua mensagem
- Enviar para o Assistant
- Quando o Assistant quiser dados do NocoDB, este código chama o servidor
- Retorna os dados para o Assistant
- Mostra a resposta final
"""