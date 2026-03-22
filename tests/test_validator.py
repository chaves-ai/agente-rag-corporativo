from src.nodes.validator import validator_node

def state_base(resposta, tentativas=0):
    return {
        "pergunta":     "O que e RAG?",
        "rota":         "rag",
        "contexto":     [],
        "fontes":       [],
        "resposta":     resposta,
        "tentativas":   tentativas,
        "qualidade_ok": False,
        "erro":         None,
    }

# Teste 1 — resposta curta deve reprovar
state = state_base("Nao sei.")
resultado = validator_node(state)
assert resultado["qualidade_ok"] == False
assert resultado["tentativas"] == 1
print("Teste 1 OK — resposta curta reprovada")

# Teste 2 — frase de falha deve reprovar
state = state_base("Nao encontrei informacoes sobre esse assunto nos documentos.")
resultado = validator_node(state)
assert resultado["qualidade_ok"] == False
print("Teste 2 OK — frase de falha reprovada")

# Teste 3 — resposta boa deve aprovar
state = state_base("RAG significa Retrieval-Augmented Generation. "
                   "E uma tecnica que combina busca em documentos com "
                   "geracao de texto por LLMs para reduzir alucinacoes.")
resultado = validator_node(state)
assert resultado["qualidade_ok"] == True
print("Teste 3 OK — resposta boa aprovada")

# Teste 4 — tentativas incrementadas corretamente
state = state_base("Nao sei.", tentativas=2)
resultado = validator_node(state)
assert resultado["tentativas"] == 3
print("Teste 4 OK — tentativas incrementadas corretamente")

print("\nTodos os testes do validator passaram!")