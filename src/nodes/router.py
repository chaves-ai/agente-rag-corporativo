from src.state.agent_state import AgentState

palavras_sql = [
    # Agregações
    "total", "media", "soma", "quantidade",
    "faturamento", "receita", "lucro", "custo",
    # Comparações de dados
    "vendeu mais", "vendeu menos", "maior venda",
    "menor venda", "mais vendas", "menos vendas",
    "melhor vendedor", "ranking", "top",
    # Campos do banco
    "salario", "salarial", "vendas", "vendedor",
    "departamento", "colaborador", "funcionario",
    # Filtros numéricos
    "quanto", "quantos", "valor", "preco",
]

palavras_rag = [
    # Políticas e documentos
    "politica", "regra", "norma", "procedimento",
    "como funciona", "o que e", "qual e",
    "posso", "tenho direito", "como solicitar",
    "prazo", "permitido", "obrigatorio",
    # Temas do documento
    "home office", "ferias", "reembolso",
    "treinamento", "avaliacao", "desempenho",
    "auxilio", "bonus", "abono",
]

def router_node(state: AgentState) -> AgentState:
    pergunta = state["pergunta"].lower()

    # RAG tem prioridade — verifica primeiro
    if any(palavra in pergunta for palavra in palavras_rag):
        state["rota"] = "rag"
    elif any(palavra in pergunta for palavra in palavras_sql):
        state["rota"] = "sql"
    else:
        state["rota"] = "rag"

    print(f"[ROUTER] Pergunta: '{state['pergunta']}'")
    print(f"[ROUTER] Rota escolhida: '{state['rota']}'")
    return state