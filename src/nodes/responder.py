from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from src.state.agent_state import AgentState
from src.config import TEMPERATURA

# ── SINGLETON — modelo carregado uma vez ────────────────
_modelo = None

def get_modelo():
    global _modelo
    if _modelo is None:
        _modelo = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=TEMPERATURA
        )
        print("[RESPONDER] Modelo LLM carregado e em cache")
    return _modelo

# ── SYSTEM PROMPTS por rota ──────────────────────────────
SYSTEM_RAG = SystemMessage(content=
    "Voce e um assistente corporativo preciso. "
    "Responda APENAS com base nos trechos fornecidos. "
    "Se a informacao nao estiver nos trechos, diga: "
    "'Nao encontrei essa informacao nos documentos disponiveis.' "
    "Cite qual trecho usou. Seja direto e objetivo."
)

SYSTEM_SQL = SystemMessage(content=
    "Voce e um assistente corporativo de dados. "
    "Os dados abaixo sao resultado EXATO de uma consulta no banco da empresa. "
    "Esses numeros sao reais e corretos. "
    "Interprete e responda de forma direta usando os dados fornecidos. "
    "Use formato brasileiro para valores monetarios (R$)."
)

SYSTEM_GERAL = SystemMessage(content=
    "Voce e um assistente corporativo. "
    "Responda de forma clara e objetiva. "
    "Se nao souber, diga que nao tem essa informacao."
)

def responder_node(state: AgentState) -> AgentState:
    pergunta  = state["pergunta"]
    contexto  = state["contexto"]
    fontes    = state["fontes"]
    historico = state["historico"]
    rota      = state["rota"]

    # ── MONTA O PROMPT E ESCOLHE O SYSTEM ───────────────
    if rota == "sql" and contexto:
        system = SYSTEM_SQL
        prompt = (
            f"DADOS DO BANCO:\n{contexto[0]}\n\n"
            f"PERGUNTA: {pergunta}\n\n"
            f"RESPOSTA:"
        )

    elif contexto:
        system = SYSTEM_RAG
        trechos = "\n\n".join(
            f"[Trecho {i+1}]: {t}"
            for i, t in enumerate(contexto)
        )
        prompt = (
            f"TRECHOS:\n{trechos}\n\n"
            f"PERGUNTA: {pergunta}\n\n"
            f"RESPOSTA:"
        )

    else:
        system = SYSTEM_GERAL
        prompt = (
            f"PERGUNTA: {pergunta}\n\n"
            f"RESPOSTA:"
        )

    print(f"[RESPONDER] Gerando resposta para: '{pergunta}'")
    print(f"[RESPONDER] Rota: {rota} | Contexto: {len(contexto)} chunks")
    print(f"[RESPONDER] Historico: {len(historico)} mensagens anteriores")

    # ── SYSTEM CORRETO + HISTORICO + PERGUNTA ───────────
    mensagens = [system] + historico + [HumanMessage(content=prompt)]
    resposta  = get_modelo().invoke(mensagens)

    state["resposta"] = resposta.content
    print(f"[RESPONDER] Resposta gerada com sucesso")
    return state