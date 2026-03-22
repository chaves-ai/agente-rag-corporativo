from src.rag.chunker import processar_pasta
from src.rag.embeddings import get_ou_criar_collection
from src.config import TOP_K_RESULTS

SCORE_MINIMO = 0.3

def indexar_documentos():
    print("\n[RETRIEVER] Iniciando indexacao...")
    colecao, embedding_fn = get_ou_criar_collection()

    if colecao.count() > 0:
        print(f"[RETRIEVER] Ja indexado — {colecao.count()} chunks")
        return colecao, embedding_fn

    chunks = processar_pasta()

    textos    = [c.page_content for c in chunks]
    metadados = [c.metadata     for c in chunks]
    ids       = [f"chunk_{i}"   for i in range(len(chunks))]

    embeddings = embedding_fn.embed_documents(textos)

    colecao.add(
        documents=textos,
        embeddings=embeddings,
        metadatas=metadados,
        ids=ids,
    )
    print(f"[RETRIEVER] {len(chunks)} chunks indexados com sucesso")
    return colecao, embedding_fn

def buscar(pergunta: str):
    colecao, embedding_fn = indexar_documentos()

    vetor_pergunta = embedding_fn.embed_query(pergunta)

    resultados = colecao.query(
        query_embeddings=[vetor_pergunta],
        n_results=TOP_K_RESULTS,
        include=["documents", "distances", "metadatas"]
    )

    documentos = resultados["documents"][0]
    distancias = resultados["distances"][0]
    metadados  = resultados["metadatas"][0]

    # Converte distancia em score de similaridade
    # ChromaDB retorna distancia cosine — menor = mais similar
    # Score = 1 - distancia  (0 a 1, maior = mais relevante)
    chunks_com_score = []
    for doc, dist, meta in zip(documentos, distancias, metadados):
        score = round(1 - dist, 4)
        chunks_com_score.append({
            "texto":  doc,
            "score":  score,
            "fonte":  meta.get("source", "documento_interno"),
        })

    # Filtra por score minimo
    antes   = len(chunks_com_score)
    chunks_com_score = [c for c in chunks_com_score
                        if c["score"] >= SCORE_MINIMO]
    depois  = len(chunks_com_score)

    print(f"[RETRIEVER] {antes} chunks encontrados")
    print(f"[RETRIEVER] {depois} chunks acima do score minimo ({SCORE_MINIMO})")

    for i, chunk in enumerate(chunks_com_score):
        print(f"[RETRIEVER] Chunk {i+1} | score: {chunk['score']} | "
              f"'{chunk['texto'][:50]}...'")

    return chunks_com_score