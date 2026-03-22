from langchain_huggingface import HuggingFaceEmbeddings
from src.config import VECTOR_STORE
import chromadb
from chromadb.config import Settings

MODELO_EMBEDDING = "all-MiniLM-L6-v2"
COLLECTION_NAME  = "documentos_corporativos"

# ── SINGLETON — carrega o modelo uma única vez ──────────
_embedding_fn = None

def get_embedding_function():
    global _embedding_fn
    if _embedding_fn is None:
        print(f"[EMBEDDINGS] Carregando modelo: {MODELO_EMBEDDING}")
        _embedding_fn = HuggingFaceEmbeddings(model_name=MODELO_EMBEDDING)
        print(f"[EMBEDDINGS] Modelo carregado e em cache")
    else:
        print(f"[EMBEDDINGS] Usando modelo em cache")
    return _embedding_fn

def get_cliente_chroma():
    return chromadb.PersistentClient(
        path=VECTOR_STORE,
        settings=Settings(anonymized_telemetry=False)
    )

def get_ou_criar_collection():
    cliente      = get_cliente_chroma()
    embedding_fn = get_embedding_function()

    colecao = cliente.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    print(f"[EMBEDDINGS] Collection: {COLLECTION_NAME}")
    print(f"[EMBEDDINGS] Documentos indexados: {colecao.count()}")
    return colecao, embedding_fn