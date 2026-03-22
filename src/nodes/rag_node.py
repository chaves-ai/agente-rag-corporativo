from src.rag.retriever import buscar
from src.state.agent_state import AgentState

SCORE_EXIBICAO = 0.5

def rag_node(state: AgentState) -> AgentState:
    pergunta = state["pergunta"]

    print(f"[RAG] Buscando documentos para: '{pergunta}'")

    chunks_com_score = buscar(pergunta)

    if not chunks_com_score:
        print(f"[RAG] Nenhum documento relevante encontrado")
        state["contexto"]     = []
        state["fontes"]       = []
        state["contexto_rag"] = []
        state["fontes_rag"]   = []
        return state

    textos = [c["texto"] for c in chunks_com_score]
    fontes = [f"{c['fonte']} (score: {c['score']})"
              for c in chunks_com_score]

    bons = [c for c in chunks_com_score if c["score"] >= SCORE_EXIBICAO]
    print(f"[RAG] {len(bons)} chunks de alta qualidade (score >= {SCORE_EXIBICAO})")

    # Salva em contexto E contexto_rag
    state["contexto"]     = textos
    state["fontes"]       = fontes
    state["contexto_rag"] = textos
    state["fontes_rag"]   = fontes

    print(f"[RAG] {len(textos)} chunks carregados")
    return state