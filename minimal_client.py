"""
Cliente NocoDB Minimalista - Sem OpenAI, sem complicação!
"""

import requests
import json

# URL do servidor
API = 'https://nocodbclaudecode-production.up.railway.app/execute'

# Função simples para chamar API
def nocodb(tool, args=None):
    response = requests.post(API, json={'tool': tool, 'args': args or {}})
    return response.json()

# Exemplos de uso
if __name__ == "__main__":
    print("=== NocoDB Client ===\n")
    
    # 1. Listar bases
    print("1. Listando bases:")
    bases = nocodb('list_bases')
    for base in bases['result']['list']:
        print(f"   - {base['title']} (ID: {base['id']})")
    
    # 2. Listar tabelas (use um ID de base real)
    print("\n2. Listando tabelas da primeira base:")
    if bases['result']['list']:
        base_id = bases['result']['list'][0]['id']
        tables = nocodb('list_tables', {'base_id': base_id})
        print(json.dumps(tables, indent=2))
    
    # 3. Criar registro (exemplo)
    print("\n3. Para criar um registro:")
    print("   nocodb('create_record', {")
    print("       'table_id': 'seu_table_id',")
    print("       'record_data': {'nome': 'João', 'email': 'joao@email.com'}")
    print("   })")
    
    # 4. Modo interativo
    print("\n4. Modo interativo (digite 'sair' para terminar)")
    while True:
        print("\nOperações disponíveis:")
        print("  - list_bases")
        print("  - list_tables (precisa base_id)")
        print("  - list_records (precisa table_id)")
        print("  - create_record (precisa table_id e record_data)")
        
        op = input("\nDigite a operação: ").strip()
        if op.lower() == 'sair':
            break
            
        args_str = input("Digite os argumentos (JSON) ou deixe vazio: ").strip()
        args = json.loads(args_str) if args_str else {}
        
        try:
            result = nocodb(op, args)
            print("\nResultado:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"\nErro: {e}")

"""
COMO USAR:

1. Instale requests:
   pip install requests

2. Execute:
   python minimal_client.py

3. Pronto! Sem OpenAI, sem complicação.
"""