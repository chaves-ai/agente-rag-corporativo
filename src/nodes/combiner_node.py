from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from src.state.agent_state import AgentState
from src.config import TEMPERATURA

modelo = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=TEMPERATURA
)

def combiner_node(state: AgentState) -> AgentState:
    pergunta     = state["pergunta"]
    contexto_rag = state["contexto_rag"]
    contexto_sql = state["contexto_sql"]
    historico    = state["historico"]

    print(f"[COMBINER] Combinando RAG e SQL")
    print(f"[COMBINER] Chunks RAG: {len(contexto_rag)}")
    print(f"[COMBINER] Chunks SQL: {len(contexto_sql)}")

    # Monta o contexto combinado
    secoes = []

    if contexto_rag:
        rag_texto = "\n\n".join([
            f"[Documento {i+1}]: {texto}"
            for i, texto in enumerate(contexto_rag)
        ])
        secoes.append(f"INFORMACOES DOS DOCUMENTOS:\n{rag_texto}")

    if contexto_sql:
        secoes.append(f"DADOS DO BANCO:\n{contexto_sql[0]}")

    contexto_completo = "\n\n" + "\n\n".join(secoes)

    prompt = f"""Voce e um assistente corporativo completo.

Responda a pergunta usando TODAS as informacoes abaixo.
Integre os dados numericos com as informacoes dos documentos.
Seja claro, direto e cite as fontes quando relevante.
{contexto_completo}

PERGUNTA: {pergunta}

RESPOSTA INTEGRADA:"""

    print(f"[COMBINER] Gerando resposta integrada...")
    mensagens = historico + [HumanMessage(content=prompt)]
    resposta  = modelo.invoke(mensagens)

    state["resposta"] = resposta.content
    state["contexto"] = contexto_rag + contexto_sql
    state["fontes"]   = state["fontes_rag"] + state["fontes_sql"]
    state["rota"]     = "combinado"  # ← adiciona essa linha

    print(f"[COMBINER] Resposta integrada gerada")
    return state