from src.rag.chunker import processar_pasta
from src.rag.embeddings import get_ou_criar_collection, get_embedding_function

print("Iniciando reindexacao...")
colecao, embedding_fn = get_ou_criar_collection()

if colecao.count() > 0:
    colecao.delete(ids=colecao.get()['ids'])
    print("[REINDEX] Collection limpa.")

chunks = processar_pasta()
texts = [c.page_content for c in chunks]
metas = [c.metadata for c in chunks]
ids   = [str(i) for i in range(len(chunks))]

print(f"Gerando embeddings para {len(chunks)} chunks...")
embeddings = list(embedding_fn.embed(texts))
embeddings = [e.tolist() for e in embeddings]

colecao.add(
    documents=texts,
    metadatas=metas,
    ids=ids,
    embeddings=embeddings
)
print(f"Indexados: {colecao.count()} chunks")
print("Reindexacao concluida!")