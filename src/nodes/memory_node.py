from langchain_core.messages import HumanMessage, AIMessage
from src.state.agent_state import AgentState

MAX_HISTORICO = 10

def memory_node(state: AgentState) -> AgentState:
    pergunta = state["pergunta"]
    resposta = state["resposta"]
    historico = state["historico"]

    print(f"[MEMORY] Salvando par pergunta/resposta")
    print(f"[MEMORY] Historico atual: {len(historico)} mensagens")

    # Adiciona a pergunta atual e a resposta ao historico
    historico.append(HumanMessage(content=pergunta))
    historico.append(AIMessage(content=resposta))

    # Limita o tamanho do historico
    if len(historico) > MAX_HISTORICO:
        historico = historico[-MAX_HISTORICO:]
        print(f"[MEMORY] Historico truncado para {MAX_HISTORICO} mensagens")

    state["historico"] = historico

    print(f"[MEMORY] Historico atualizado: {len(historico)} mensagens")
    return state