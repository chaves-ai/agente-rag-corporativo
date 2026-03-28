from src.rag.retriever import buscar, indexar_documentos

print("=== Teste do Pipeline RAG Avancado ===\n")

# Teste 1 — indexacao
print("Teste 1 — Indexando documentos...")
colecao, _ = indexar_documentos()
assert colecao.count() > 0, "ERRO: nenhum chunk indexado"
print(f"Teste 1 OK — {colecao.count()} chunks indexados\n")

# Teste 2 — busca com score
print("Teste 2 — Busca com score de relevancia...")
chunks = buscar("Qual o prazo para solicitar reembolso?")
assert len(chunks) > 0, "ERRO: nenhum chunk retornado"
assert "score" in chunks[0], "ERRO: score nao encontrado"
assert "texto" in chunks[0], "ERRO: texto nao encontrado"
assert "fonte" in chunks[0], "ERRO: fonte nao encontrada"
print(f"Teste 2 OK — {len(chunks)} chunks com score")
print(f"  Melhor score: {chunks[0]['score']}")
print(f"  Chunk: '{chunks[0]['texto'][:60]}...'\n")

# Teste 3 — scores em ordem decrescente
print("Teste 3 — Scores em ordem decrescente...")
chunks = buscar("politica de ferias")
scores = [c["score"] for c in chunks]
assert scores == sorted(scores, reverse=True), \
    "ERRO: chunks nao estao ordenados por score"
print(f"Teste 3 OK — scores ordenados: {scores}\n")

# Teste 4 — filtro por score minimo
print("Teste 4 — Filtro por score minimo...")
chunks = buscar("home office auxilio internet")
for chunk in chunks:
    assert chunk["score"] >= 0.3, \
        f"ERRO: chunk com score abaixo do minimo: {chunk['score']}"
print(f"Teste 4 OK — todos os chunks acima do score minimo\n")

print("=== Todos os testes RAG avancado passaram! ===")