from src.state.agent_state import AgentState
from src.utils.avaliador import avaliar_completo
from src.utils.dashboard import registrar_avaliacao

TAMANHO_MINIMO = 5
MAX_TENTATIVAS = 3
SCORE_MINIMO   = 0.5

FRASES_SEM_RESPOSTA = [
    "nao encontrei essa informacao nos documentos disponiveis",
    "nao tenho informacao sobre",
    "nao foi possivel encontrar",
    "nao ha informacao disponivel",
]

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

    # Criterio 2 — agente sinalizou que nao encontrou a informacao
    # Nesse caso aprovamos imediatamente — e correto nao encontrar
    # o que nao existe nos documentos
    if any(f in resposta.lower() for f in FRASES_SEM_RESPOSTA):
        print(f"[VALIDATOR] APROVADO — agente sinalizou ausencia de informacao corretamente")
        state["qualidade_ok"] = True
        state["tentativas"]   = tentativas + 1
        state["metricas"]     = {}
        state["score_geral"]  = 1.0
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