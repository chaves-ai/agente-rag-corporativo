# Agente RAG Corporativo

> Sistema de Inteligência Artificial para consulta de documentos e dados corporativos em linguagem natural.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-latest-green)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-teal)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![LangSmith](https://img.shields.io/badge/LangSmith-monitored-orange)

---

## O que é

O Agente RAG Corporativo é um sistema de IA que permite que colaboradores façam perguntas em português sobre os documentos internos e banco de dados da empresa — e recebem respostas precisas, rastreáveis e auditáveis.

**Sem inventar informações. Sem consultar a internet. Apenas os seus dados.**

---

## Funcionalidades

- Consulta inteligente de documentos internos (PDFs, TXTs, Word)
- Consulta de banco de dados em linguagem natural (SQL gerado automaticamente)
- Respostas híbridas combinando documentos e dados simultaneamente
- Memória de conversa por usuário (sessões independentes)
- Avaliação automática de qualidade com score auditável
- API REST completa com documentação automática
- Interface web profissional sem necessidade de conhecimento técnico
- Monitoramento em tempo real via LangSmith
- Deploy em Docker com um único comando

---

## Stack tecnológica

| Camada | Tecnologia | Função |
|--------|-----------|--------|
| Orquestração | LangGraph | Controle do fluxo entre agentes |
| LLM | Groq (llama-3.3-70b) | Geração de respostas |
| Embeddings | HuggingFace (all-MiniLM-L6-v2) | Busca semântica local |
| Banco Vetorial | ChromaDB | Indexação de documentos |
| Banco Relacional | SQLite / PostgreSQL | Dados estruturados |
| API | FastAPI | Interface REST |
| Infraestrutura | Docker + Docker Compose | Deploy e portabilidade |
| Monitoramento | LangSmith | Rastreamento e auditoria |

---

## Início rápido

### Pré-requisitos

- Docker Desktop instalado
- Chave de API Groq (gratuita em console.groq.com)

### Instalação
```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/agente-rag-corporativo.git
cd agente-rag-corporativo

# 2. Configure as variáveis de ambiente
cp .env.exemplo .env
# Edite o .env com suas chaves de API

# 3. Adicione seus documentos
# Coloque arquivos .txt, .pdf ou .docx em:
data/raw/

# 4. Suba o sistema
docker-compose up -d

# 5. Acesse a documentação
http://localhost:8000/docs
```

### Testando

Acesse `http://localhost:8000/docs` e teste o endpoint `POST /agente/perguntar`:
```json
{
  "pergunta": "Qual a política de home office?",
  "session_id": "meu_usuario"
}
```

---

## Estrutura do projeto
```
agente-rag-corporativo/
├── api/                    # FastAPI — endpoints REST
│   ├── main_api.py         # Aplicação principal
│   ├── schemas.py          # Modelos de dados
│   └── routers/
│       └── agente.py       # Endpoints do agente
├── src/
│   ├── config.py           # Configurações centralizadas
│   ├── state/              # Estado do agente (LangGraph)
│   ├── nodes/              # Nós do grafo
│   │   ├── router.py       # Roteamento de perguntas
│   │   ├── rag_node.py     # Busca em documentos
│   │   ├── sql_node.py     # Consulta SQL
│   │   ├── responder.py    # Geração de respostas
│   │   ├── validator.py    # Avaliação de qualidade
│   │   └── memory_node.py  # Memória de conversa
│   ├── graphs/
│   │   └── main_graph.py   # Grafo principal LangGraph
│   ├── rag/                # Pipeline RAG
│   │   ├── chunker.py      # Divisão de documentos
│   │   ├── embeddings.py   # Vetorização
│   │   └── retriever.py    # Recuperação com score
│   ├── tools/
│   │   └── sql_tool.py     # Geração e execução de SQL
│   └── utils/
│       ├── avaliador.py    # Métricas de qualidade
│       └── dashboard.py    # Dashboard de métricas
├── data/
│   ├── raw/                # Documentos do cliente
│   ├── vector_store/       # ChromaDB (gerado automaticamente)
│   └── banco_corporativo.db # Banco de dados SQLite
├── tests/                  # Testes automatizados
├── scripts/                # Scripts utilitários
├── Dockerfile              # Configuração do container
├── docker-compose.yml      # Orquestração de serviços
└── .env.exemplo            # Modelo de configuração
```

---

## Arquitetura do fluxo
```
Pergunta do usuário
        ↓
    Router
    /    \
  RAG    SQL
   |      |
Busca  Consulta
vetorial  banco
   \      /
   Combiner (se híbrido)
        ↓
    Responder
        ↓
    Validator (score automático)
        ↓
    Memory (salva histórico)
        ↓
   Resposta final
```

---

## Métricas de qualidade

O sistema avalia automaticamente cada resposta em 3 dimensões:

| Métrica | O que mede | Meta |
|---------|-----------|------|
| Faithfulness | Resposta baseada nos documentos | > 0.8 |
| Relevância | Resposta responde a pergunta | > 0.8 |
| Precisão | Contexto recuperado é relevante | > 0.7 |
| Score geral | Média ponderada | > 0.8 |

**Resultados obtidos em produção: Score médio 0.97**

---

## Custos de infraestrutura

| Componente | Custo mensal |
|-----------|-------------|
| Embeddings (local) | R$ 0,00 |
| ChromaDB (local) | R$ 0,00 |
| Groq LLM (plano gratuito) | R$ 0,00 |
| Servidor (DigitalOcean 4GB) | R$ 70,00 |
| **Total** | **R$ 70,00/mês** |

---

## Configuração do .env
```env
# LLM
GROQ_API_KEY=sua_chave_groq
TEMPERATURA=0

# LangSmith (opcional — monitoramento)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=sua_chave_langsmith
LANGCHAIN_PROJECT=agente-rag-corporativo
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

---

## Endpoints da API

| Método | Endpoint | Descrição |
|--------|---------|-----------|
| POST | /agente/perguntar | Envia pergunta e recebe resposta |
| GET | /agente/metricas | Dashboard de qualidade |
| DELETE | /agente/sessao/{id} | Limpa histórico de sessão |
| GET | /health | Status do sistema |
| GET | /docs | Documentação interativa |

---

## Licença

MIT License — livre para uso comercial e modificação.

---

## Autor

Desenvolvido como projeto de estudo e aplicação profissional em IA Corporativa.