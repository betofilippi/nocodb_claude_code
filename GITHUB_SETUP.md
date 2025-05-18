# Como publicar no GitHub

## 1. Criar repositório no GitHub

1. Acesse https://github.com/new
2. Nome do repositório: `nocodb_claude_code`
3. Descrição: "NocoDB MCP Server - Integração completa com Claude Code"
4. Visibilidade: Público
5. NÃO inicialize com README, .gitignore ou licença
6. Clique em "Create repository"

## 2. Configurar SSH (se necessário)

```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "adm@nxt.eco.br"

# Copiar chave pública
cat ~/.ssh/id_ed25519.pub

# Adicionar no GitHub: Settings > SSH and GPG keys > New SSH key
```

## 3. Enviar código para o GitHub

```bash
cd /home/betofilippi/projects/nocodb_mcp_full

# Se usar SSH
git remote add origin git@github.com:betofilippi/nocodb_claude_code.git

# Se usar HTTPS (precisará de token)
git remote add origin https://github.com/betofilippi/nocodb_claude_code.git

# Enviar código
git push -u origin main
```

## 4. Se usar HTTPS, criar Personal Access Token

1. GitHub > Settings > Developer settings > Personal access tokens
2. Generate new token (classic)
3. Permissões: repo (full control)
4. Copiar token e usar como senha

## 5. Alternativa: GitHub CLI

```bash
# Instalar GitHub CLI
sudo apt install gh

# Autenticar
gh auth login

# Criar repositório
gh repo create betofilippi/nocodb_claude_code --public --source=. --remote=origin --push
```

## Estrutura do Repositório

```
nocodb_claude_code/
├── mcp_nocodb_server_full.py   # Servidor completo
├── requirements.txt            # Dependências
├── README.md                   # Documentação
├── LICENSE                     # MIT License
├── .env.example               # Exemplo de configuração
└── .gitignore                 # Arquivos ignorados
```