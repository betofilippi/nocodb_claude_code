from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

BASE_URL = "https://planilha.plataforma.app/api/v1/db"
API_KEY = "6PXQIre9nyqukms7OsbUNMPYLsptIVLBgBHe30Jb"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_from_nocodb(endpoint):
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()

def post_to_nocodb(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code not in [200, 201]:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()

@app.get("/status")
def status():
    return get_from_nocodb("/meta/nocodb/info")

@app.get("/projetos")
def listar_projetos():
    return get_from_nocodb("/meta/projects")

@app.get("/projeto/{projeto}/tabelas")
def listar_tabelas(projeto: str):
    return get_from_nocodb(f"/meta/projects/{projeto}/tables")

@app.get("/projeto/{projeto}/tabela/{tabela}/registros")
def listar_registros(projeto: str, tabela: str):
    return get_from_nocodb(f"/data/{projeto}/{tabela}")

@app.post("/projeto/{projeto}/tabela/{tabela}/registros")
def criar_registro(projeto: str, tabela: str, registro: dict):
    return post_to_nocodb(f"/data/{projeto}/{tabela}", registro)

@app.get("/projeto/{projeto}/tabela/{tabela}/registro/{id_registro}")
def obter_registro(projeto: str, tabela: str, id_registro: str):
    return get_from_nocodb(f"/data/{projeto}/{tabela}/{id_registro}")

@app.get("/projeto/{projeto}/views")
def listar_views(projeto: str):
    return get_from_nocodb(f"/meta/projects/{projeto}/views")

@app.get("/projeto/{projeto}/plugins")
def listar_plugins(projeto: str):
    return get_from_nocodb(f"/meta/projects/{projeto}/plugins")

@app.get("/projeto/{projeto}/webhooks")
def listar_webhooks(projeto: str):
    return get_from_nocodb(f"/meta/projects/{projeto}/webhooks")

@app.get("/projeto/{projeto}/colunas/{tabela}")
def listar_colunas(projeto: str, tabela: str):
    return get_from_nocodb(f"/meta/projects/{projeto}/tables/{tabela}/columns")

@app.get("/usuarios")
def listar_usuarios():
    return get_from_nocodb("/meta/users")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080)