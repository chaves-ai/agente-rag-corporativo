from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from src.state.agent_state import AgentState
from src.config import TEMPERATURA

modelo = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

def analyzer_node(state: AgentState) -> AgentState:
    pergunta = state["pergunta"]

    print(f"[ANALYZER] Analisando pergunta: '{pergunta}'")

    prompt = f"""Analise a pergunta abaixo e determine quais fontes de dados sao necessarias.

FONTES DISPONIVEIS:
- RAG: documentos internos, politicas, regras, normas, procedimentos
- SQL: dados numericos, vendas, salarios, metricas, rankings, totais

Responda APENAS com um JSON no formato:
{{"precisa_rag": true/false, "precisa_sql": true/false}}

Exemplos:
"Qual a politica de ferias?" → {{"precisa_rag": true, "precisa_sql": false}}
"Qual o total de vendas?" → {{"precisa_rag": false, "precisa_sql": true}}
"Quem vendeu mais e qual e a meta de desempenho?" → {{"precisa_rag": true, "precisa_sql": true}}

PERGUNTA: {pergunta}

JSON:"""

    resposta = modelo.invoke([HumanMessage(content=prompt)])
    texto    = resposta.content.strip()

    # Parse do JSON
    import json
    try:
        texto_limpo = texto.replace("```json", "").replace("```", "").strip()
        decisao     = json.loads(texto_limpo)
        precisa_rag = decisao.get("precisa_rag", False)
        precisa_sql = decisao.get("precisa_sql", False)
    except:
        # Se falhar o parse — usa o router como fallback
        print(f"[ANALYZER] Falha no parse — usando fallback")
        precisa_rag = state["rota"] == "rag"
        precisa_sql = state["rota"] == "sql"

    state["precisa_rag"] = precisa_rag
    state["precisa_sql"] = precisa_sql

    print(f"[ANALYZER] precisa_rag: {precisa_rag}")
    print(f"[ANALYZER] precisa_sql: {precisa_sql}")
    return state