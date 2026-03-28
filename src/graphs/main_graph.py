from langgraph.graph import StateGraph, END
from src.state.agent_state import AgentState
from src.nodes.router import router_node
from src.nodes.analyzer_node import analyzer_node
from src.nodes.rag_node import rag_node
from src.nodes.sql_node import sql_node
from src.nodes.combiner_node import combiner_node
from src.nodes.responder import responder_node
from src.nodes.validator import validator_node, MAX_TENTATIVAS
from src.nodes.memory_node import memory_node

def construir_grafo():
    grafo = StateGraph(AgentState)

    # Registra todos os nos
    grafo.add_node("router",    router_node)
    grafo.add_node("analyzer",  analyzer_node)
    grafo.add_node("rag",       rag_node)
    grafo.add_node("sql",       sql_node)
    grafo.add_node("combiner",  combiner_node)
    grafo.add_node("responder", responder_node)
    grafo.add_node("validator", validator_node)
    grafo.add_node("memory",    memory_node)

    # Entrada pelo router
    grafo.set_entry_point("router")

    # Router — decide o primeiro no
    def decisao_router(state: AgentState) -> str:
        pergunta = state["pergunta"].lower()
        palavras_complexas = [
            "e qual", "e tambem", "alem disso",
            "e como", "mas qual", "e o que",
            "quanto e", "e quando", "e quem"
        ]
        if any(p in pergunta for p in palavras_complexas):
            return "complexo"
        return state["rota"]

    grafo.add_conditional_edges(
        "router",
        decisao_router,
        {
            "rag":      "rag",
            "sql":      "sql",
            "complexo": "analyzer",
        }
    )

    # Analyzer — sempre vai para RAG primeiro
    def decisao_analyzer(state: AgentState) -> str:
        if state["precisa_rag"]:
            return "rag"
        return "sql"

    grafo.add_conditional_edges(
        "analyzer",
        decisao_analyzer,
        {
            "rag": "rag",
            "sql": "sql",
        }
    )

    # RAG — decide proximo passo
    def decisao_apos_rag(state: AgentState) -> str:
        # Fluxo complexo: precisa de SQL depois do RAG
        if state["precisa_sql"] and state["precisa_rag"]:
            return "sql"
        # Fluxo simples: vai direto pro responder
        return "responder"

    grafo.add_conditional_edges(
        "rag",
        decisao_apos_rag,
        {
            "sql":      "sql",
            "responder": "responder",
        }
    )

    # SQL — decide proximo passo
    def decisao_apos_sql(state: AgentState) -> str:
        tem_rag    = len(state.get("contexto_rag", [])) > 0
        precisa_rag = state.get("precisa_rag", False)

        print(f"[GRAFO] apos_sql — precisa_rag: {precisa_rag} | tem_rag: {tem_rag}")

        if precisa_rag and tem_rag:
            return "combiner"
        return "responder"

    grafo.add_conditional_edges(
        "sql",
        decisao_apos_sql,
        {
            "combiner":  "combiner",
            "responder": "responder",
        }
    )

    # Combiner e responder — sempre vao para validator
    grafo.add_edge("combiner",  "validator")
    grafo.add_edge("responder", "validator")

    # Validator — decide proximo passo
    def decisao_validator(state: AgentState) -> str:
        if state["qualidade_ok"]:
            return "aprovado"
        if state["tentativas"] >= MAX_TENTATIVAS:
            return "limite"
        return "tentar_novamente"

    grafo.add_conditional_edges(
        "validator",
        decisao_validator,
        {
            "aprovado":         "memory",
            "limite":           "memory",
            "tentar_novamente": "responder",
        }
    )

    grafo.add_edge("memory", END)
    return grafo.compile()

grafo = construir_grafo()