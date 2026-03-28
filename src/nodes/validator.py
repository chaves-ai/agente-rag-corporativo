from src.state.agent_state import AgentState
from src.utils.avaliador import avaliar_completo
from src.utils.dashboard import registrar_avaliacao

TAMANHO_MINIMO = 5
MAX_TENTATIVAS = 3
SCORE_MINIMO   = 0.5

def validator_node(state: AgentState) -> AgentState:
    resposta   = state["resposta"]
    tentativas = state["tentativas"]
    pergunta   = state["pergunta"]
    contexto   = state["contexto"]
    rota       = state["rota"]

    print(f"[VALIDATOR] Tentativa {tentativas + 1} de {MAX_TENTATIVAS}")
    print(f"[VALIDATOR] Tamanho da resposta: {len(resposta)} caracteres")

    # Criterio 1 — tamanho minimo
    if len(resposta) < TAMANHO_MINIMO:
        print(f"[VALIDATOR] REPROVADO — resposta muito curta")
        state["qualidade_ok"] = False
        state["tentativas"]   = tentativas + 1
        state["metricas"]     = {}
        state["score_geral"]  = 0.0
        return state

    # Criterio 2 — frases de falha
    frases_falha = [
        "nao encontrei essa informacao nos documentos disponiveis",
        "nao tenho informacao sobre",
        "nao foi possivel encontrar",
    ]
    if any(f in resposta.lower() for f in frases_falha) and len(resposta) < 200:
        print(f"[VALIDATOR] REPROVADO — resposta indica falha")
        state["qualidade_ok"] = False
        state["tentativas"]   = tentativas + 1
        state["metricas"]     = {}
        state["score_geral"]  = 0.0
        return state

    # Criterio 3 — avaliacao por LLM
    metricas = avaliar_completo(pergunta, contexto, resposta)
    registrar_avaliacao(pergunta, resposta, metricas, rota)

    state["metricas"]    = metricas
    state["score_geral"] = metricas["score_geral"]

    if metricas["score_geral"] >= SCORE_MINIMO:
        print(f"[VALIDATOR] APROVADO — score: {metricas['score_geral']}")
        state["qualidade_ok"] = True
    else:
        print(f"[VALIDATOR] REPROVADO — score baixo: {metricas['score_geral']}")
        state["qualidade_ok"] = False

    state["tentativas"] = tentativas + 1
    return state