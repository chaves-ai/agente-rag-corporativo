# Arquitetura do Sistema

## Visão Geral

O Agente RAG Corporativo é construído sobre 7 camadas independentes
que se comunicam via estado compartilhado (LangGraph AgentState).

---

## O Grafo LangGraph
```
ENTRADA
   ↓
[router] → decide a rota com base na pergunta
   ↓
   ├── "rag"      → [rag_node] → [responder]
   ├── "sql"      → [sql_node] → [responder]
   └── "complexo" → [analyzer] → [rag_node] + [sql_node] → [combiner] → [responder]
                                                                              ↓
                                                                        [validator]
                                                                              ↓
                                                                    aprovado → [memory] → FIM
                                                                    reprovado → [responder] (nova tentativa)
```

---

## Decisões de Arquitetura

### Por que LangGraph e não LangChain simples?

LangChain simples é linear — A chama B chama C.
LangGraph permite grafos com condicionais, loops e estado compartilhado.
O validator pode redirecionar para o responder até 3 vezes.
Isso não é possível em LangChain simples.

### Por que ChromaDB local e não Pinecone?

ChromaDB roda no servidor do cliente — zero custo por consulta.
Pinecone é um serviço externo — custo variável e dados saem da empresa.
Para dados corporativos sensíveis, local é sempre preferível.

### Por que Groq e não OpenAI?

Groq tem plano gratuito generoso — 14.400 requisições/dia.
Latência menor que OpenAI para o modelo llama-3.3-70b.
Custo menor em produção quando pago.
OpenAI permanece como alternativa configurável.

### Por que SQLite e não PostgreSQL?

SQLite é suficiente para até 10.000 registros e uso médio.
Zero configuração — arquivo único portável no Docker.
Para volumes maiores, a migração para PostgreSQL é simples
— basta trocar a connection string no sql_tool.py.

---

## AgentState — o estado compartilhado
```python
class AgentState(TypedDict):
    pergunta:     str           # pergunta original do usuário
    rota:         str           # "rag", "sql" ou "complexo"
    contexto:     List[str]     # chunks RAG + resultado SQL
    fontes:       List[str]     # fontes dos chunks com scores
    resposta:     str           # resposta gerada pelo LLM
    tentativas:   int           # contador de tentativas do validator
    qualidade_ok: bool          # aprovado pelo validator?
    erro:         Optional[str] # mensagem de erro se houver
    historico:    List          # histórico de conversa
    precisa_rag:  bool          # flag do analyzer
    precisa_sql:  bool          # flag do analyzer
    contexto_rag: List[str]     # contexto específico do RAG
    contexto_sql: List[str]     # contexto específico do SQL
    metricas:     Dict          # faithfulness, relevância, precisão
    score_geral:  float         # score médio das métricas
```

---

## Pipeline RAG
```
Documento (.txt/.pdf/.docx)
        ↓
   [chunker.py]
   Divide em chunks de 500 tokens
   com overlap de 50 tokens
        ↓
   [embeddings.py]
   Converte chunks em vetores
   usando all-MiniLM-L6-v2
   (384 dimensões, local, gratuito)
        ↓
   [ChromaDB]
   Armazena vetores com metadados
   Persiste em data/vector_store/
        ↓
   [retriever.py]
   Recebe pergunta do usuário
   Converte em vetor
   Busca os 5 chunks mais similares
   Filtra por score mínimo 0.3
   Retorna chunks com scores
```

---

## Pipeline SQL
```
Pergunta em português
        ↓
   [sql_tool.py]
   LLM recebe: pergunta + schema do banco
   LLM gera: query SQL válida
        ↓
   [SQLite]
   Executa a query
   Retorna resultado em formato tabular
        ↓
   [responder.py]
   LLM interpreta o resultado
   Gera resposta em português
   com valores em formato brasileiro
```

---

## Sistema de Avaliação

Cada resposta é avaliada automaticamente em 3 dimensões:

**Faithfulness** — a resposta está baseada nos documentos?
O LLM avaliador verifica se cada afirmação da resposta
pode ser encontrada no contexto fornecido.

**Relevância** — a resposta responde à pergunta?
O LLM avaliador verifica se a resposta aborda
o que foi realmente perguntado.

**Precisão** — o contexto recuperado é relevante?
O LLM avaliador verifica se os chunks recuperados
eram os mais adequados para a pergunta.

**Score mínimo para aprovação: 0.5**
Se reprovado, o validator solicita nova tentativa
ao responder — máximo 3 tentativas.

---

## Segurança e Privacidade

- Documentos indexados localmente — não saem do servidor
- Chaves de API em variáveis de ambiente — nunca no código
- .env no .gitignore — nunca versionado
- ChromaDB persiste localmente — dados do cliente ficam na empresa
- LangSmith registra apenas metadados — não o conteúdo dos documentos