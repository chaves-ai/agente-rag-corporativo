from src.tools.sql_tool import consultar
from src.state.agent_state import AgentState

def sql_node(state: AgentState) -> AgentState:
    pergunta = state["pergunta"]

    print(f"[SQL_NODE] Consultando banco para: '{pergunta}'")

    resultado = consultar(pergunta)

    if not resultado or "Erro" in resultado:
        print(f"[SQL_NODE] Falha na consulta")
        state["contexto_sql"] = []
        state["fontes_sql"]   = []
        state["contexto"]     = []
        state["fontes"]       = []
        return state

    # Salva em contexto_sql para multi-agente
    state["contexto_sql"] = [resultado]
    state["fontes_sql"]   = ["banco_corporativo.db"]
    # Mantém compatibilidade com fluxo simples
    state["contexto"]     = [resultado]
    state["fontes"]       = ["banco_corporativo.db"]

    print(f"[SQL_NODE] Resultado carregado no contexto")
    return state