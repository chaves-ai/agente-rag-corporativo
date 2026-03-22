# Guia de Deploy

## Deploy Local (desenvolvimento)
```bash
# Clona o projeto
git clone https://github.com/seu-usuario/agente-rag-corporativo.git
cd agente-rag-corporativo

# Configura o ambiente
cp .env.exemplo .env
# Edita o .env com as chaves reais

# Adiciona documentos
# Coloca arquivos em data/raw/

# Sobe o sistema
docker-compose up -d

# Verifica os logs
docker logs agente-rag-corporativo

# Acessa a API
http://localhost:8000/docs
```

---

## Deploy em Produção (DigitalOcean)

### 1. Cria o servidor

- Acessa digitalocean.com
- Cria um Droplet Ubuntu 22.04
- Configuração mínima: 4GB RAM, 2 vCPUs
- Custo: ~R$ 70/mês

### 2. Configura o servidor
```bash
# Conecta via SSH
ssh root@IP_DO_SERVIDOR

# Instala Docker
apt update
apt install -y docker.io docker-compose

# Cria a pasta do projeto
mkdir /app && cd /app
```

### 3. Envia os arquivos
```bash
# Do seu computador local:
scp -r . root@IP_DO_SERVIDOR:/app/
```

### 4. Configura as variáveis
```bash
# No servidor:
cd /app
cp .env.exemplo .env
nano .env
# Preenche as chaves reais
```

### 5. Sobe o sistema
```bash
docker-compose up -d
docker logs agente-rag-corporativo
```

### 6. Acessa
```
http://IP_DO_SERVIDOR:8000/docs
```

---

## Comandos úteis do dia a dia
```bash
# Ver logs em tempo real
docker logs -f agente-rag-corporativo

# Reiniciar o container
docker-compose restart

# Parar o sistema
docker-compose down

# Atualizar após mudança no código
docker-compose up --build -d

# Entrar no container
docker exec -it agente-rag-corporativo bash

# Ver uso de recursos
docker stats agente-rag-corporativo
```

---

## Adicionando documentos do cliente
```bash
# Copia documentos para a pasta raw
cp /caminho/do/documento.pdf data/raw/

# Reinicia o container para reindexar
docker-compose restart

# Verifica nos logs se indexou
docker logs agente-rag-corporativo | grep "indexados"
```

---

## Troubleshooting comum

**Container não sobe**
```bash
docker logs agente-rag-corporativo
# Lê o erro e verifica o .env
```

**Resposta "não encontrei informação"**
```bash
# Verifica se o documento está em data/raw/
ls data/raw/
# Reinicia para reindexar
docker-compose restart
```

**SQL sem resultado**
```bash
# Verifica o banco
docker exec agente-rag-corporativo python -c \
"import sqlite3; conn=sqlite3.connect('data/banco_corporativo.db'); \
print(conn.execute('SELECT COUNT(*) FROM vendas').fetchone())"
```

**API lenta na primeira pergunta**
```
Normal — primeira pergunta carrega
o modelo de embeddings em cache.
A partir da segunda fica rápido.
```