from src.graphs.main_graph import grafo
from src.state.agent_state import AgentState

historico_global = []

def criar_state(pergunta: str) -> AgentState:
    return {
        "pergunta":     pergunta,
        "rota":         "",
        "contexto":     [],
        "fontes":       [],
        "resposta":     "",
        "tentativas":   0,
        "qualidade_ok": False,
        "erro":         None,
        "historico":    historico_global.copy(),
        "precisa_rag":  False,
        "precisa_sql":  False,
        "contexto_rag": [],
        "contexto_sql": [],
        "fontes_rag":   [],
        "fontes_sql":   [],
        "metricas":     {},
        "score_geral":  0.0,
    }

def perguntar(pergunta: str) -> str:
    global historico_global

    print(f"\n{'='*50}")
    print(f"PERGUNTA: {pergunta}")
    print(f"{'='*50}")

    state     = criar_state(pergunta)
    resultado = grafo.invoke(state)

    historico_global = resultado["historico"]

    print(f"{'='*50}")
    print(f"ROTA:        {resultado['rota']}")
    print(f"TENTATIVAS:  {resultado['tentativas']}")
    print(f"QUALIDADE:   {resultado['qualidade_ok']}")
    print(f"SCORE:       {resultado.get('score_geral', 0.0)}")
    print(f"HISTORICO:   {len(historico_global)} mensagens")
    print(f"{'='*50}\n")

    return resultado["resposta"]

if __name__ == "__main__":
    print("Agente RAG Corporativo — com Memoria e Avaliacao")
    print("Digite 'sair'      para encerrar")
    print("Digite 'historico' para ver o historico")
    print("Digite 'dashboard' para ver as metricas\n")

    while True:
        pergunta = input("Voce: ").strip()

        if not pergunta:
            continue

        if pergunta.lower() == "sair":
            print("Encerrando agente.")
            break

        if pergunta.lower() == "historico":
            print(f"\n--- Historico ({len(historico_global)} mensagens) ---")
            for msg in historico_global:
                tipo = "Voce" if msg.__class__.__name__ == "HumanMessage" else "Agente"
                print(f"{tipo}: {str(msg.content)[:80]}")
            print("---\n")
            continue

        if pergunta.lower() == "dashboard":
            from src.utils.dashboard import exibir_dashboard
            exibir_dashboard()
            continue

        resposta = perguntar(pergunta)
        print(f"Agente: {resposta}\n")

      