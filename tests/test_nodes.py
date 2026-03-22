from src.nodes.router import router_node

def state_base(pergunta):
    return {
        "pergunta":     pergunta,
        "rota":         "",
        "contexto":     [],
        "fontes":       [],
        "resposta":     "",
        "tentativas":   0,
        "qualidade_ok": False,
        "erro":         None,
        "historico":    [],
        "precisa_rag":  False,
        "precisa_sql":  False,
        "contexto_rag": [],
        "contexto_sql": [],
        "fontes_rag":   [],
        "fontes_sql":   [],
        "metricas":     {},
        "score_geral":  0.0,
    }

# ─── Testes 1 e 2: router_node ────────────────────────────
state = state_base("O que e RAG?")
resultado = router_node(state)
assert resultado["rota"] == "rag"
print("Teste 1 OK — rota:", resultado["rota"])

state = state_base("Qual o total de vendas?")
resultado = router_node(state)
assert resultado["rota"] == "sql"
print("Teste 2 OK — rota:", resultado["rota"])

# ─── Testes 3 e 4: responder_node ─────────────────────────
from src.nodes.responder import responder_node

print("\nTestando responder_node...")

state = state_base("O que e RAG em inteligencia artificial?")
resultado = responder_node(state)
assert len(resultado["resposta"]) > 0
print("Teste 3 OK — resposta gerada:")
print(f"  '{resultado['resposta'][:80]}...'")

state = state_base("O que e RAG?")
state["contexto"] = [
    "RAG significa Retrieval-Augmented Generation.",
    "Foi criado para reduzir alucinacoes em LLMs.",
]
resultado = responder_node(state)
assert len(resultado["resposta"]) > 0
print("Teste 4 OK — resposta com contexto:")
print(f"  '{resultado['resposta'][:80]}...'")

# ─── Teste 5: rag_node ────────────────────────────────────
from src.nodes.rag_node import rag_node

print("\nTestando rag_node...")

state = state_base("Qual o prazo para solicitar reembolso?")
resultado = rag_node(state)
assert len(resultado["contexto"]) > 0, "ERRO: contexto vazio"
assert "reembolso" in resultado["contexto"][0].lower() or \
       "colaborador" in resultado["contexto"][0].lower()
print(f"Teste 5 OK — {len(resultado['contexto'])} chunks carregados")
print(f"  Chunk 1: '{resultado['contexto'][0][:80]}...'")

# ─── Teste 6: grafo completo com RAG ──────────────────────
from src.graphs.main_graph import grafo

print("\nTestando grafo completo com RAG...")

state = state_base("Qual a politica de home office da empresa?")
resultado = grafo.invoke(state)

assert resultado["resposta"] != "", "ERRO: resposta vazia"
assert resultado["rota"] == "rag", "ERRO: devia ser rota rag"
assert resultado["qualidade_ok"] == True, "ERRO: nao aprovado"
assert len(resultado["contexto"]) > 0, "ERRO: sem contexto RAG"

print(f"Teste 6 OK — rota: {resultado['rota']}")
print(f"Chunks usados: {len(resultado['contexto'])}")
print(f"Qualidade: {resultado['qualidade_ok']}")
print(f"Resposta: '{resultado['resposta'][:120]}...'")

print("\nTodos os testes passaram!")