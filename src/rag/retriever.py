from src.rag.embeddings import get_ou_criar_collection
from src.config import TOP_K_RESULTS
import hashlib

SCORE_MINIMO = 0.3

# Cache em memoria — reseta ao reiniciar o container
_cache: dict = {}

# Palavras que indicam pergunta geral — precisa de mais contexto
PALAVRAS_GERAIS = [
    "quantas", "quantos", "total", "todas", "todos", "lista",
    "quais todas", "resumo", "geral", "completo", "inteiro",
    "semanas", "meses", "periodo", "quanto tempo"
]

def detectar_top_k(pergunta: str) -> int:
    pergunta_lower = pergunta.lower()
    if any(p in pergunta_lower for p in PALAVRAS_GERAIS):
        print(f"[RETRIEVER] Pergunta geral detectada — TOP_K ampliado para 10")
        return 10
    return TOP_K_RESULTS

def gerar_chave_cache(pergunta: str) -> str:
    return hashlib.md5(pergunta.strip().lower().encode()).hexdigest()

def buscar(pergunta: str):
    global _cache

    # Verifica cache
    chave = gerar_chave_cache(pergunta)
    if chave in _cache:
        print(f"[RETRIEVER] Cache hit — retornando resposta em cache")
        return _cache[chave]

    colecao, embedding_fn = get_ou_criar_collection()

    if colecao.count() == 0:
        print("[RETRIEVER] Collection vazia — rode o reindexar.py primeiro.")
        return []

    top_k = detectar_top_k(pergunta)
    top_k = min(top_k, colecao.count())

    vetor_pergunta = list(embedding_fn.embed([pergunta]))[0].tolist()

    resultados = colecao.query(
        query_embeddings=[vetor_pergunta],
        n_results=top_k,
        include=["documents", "distances", "metadatas"]
    )

    documentos = resultados["documents"][0]
    distancias = resultados["distances"][0]
    metadados  = resultados["metadatas"][0]

    chunks_com_score = []
    for doc, dist, meta in zip(documentos, distancias, metadados):
        score = round(1 - dist, 4)
        chunks_com_score.append({
            "texto": doc,
            "score": score,
            "fonte": meta.get("source", "documento_interno"),
        })

    chunks_com_score = [c for c in chunks_com_score if c["score"] >= SCORE_MINIMO]

    # Salva no cache
    _cache[chave] = chunks_com_score
    print(f"[RETRIEVER] {len(chunks_com_score)} chunks relevantes encontrados")
    for i, chunk in enumerate(chunks_com_score):
        print(f"[RETRIEVER] Chunk {i+1} | score: {chunk['score']} | '{chunk['texto'][:50]}...'")

    return chunks_com_score