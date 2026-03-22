from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, DATA_RAW
import os

def carregar_documento(caminho: str):
    print(f"[CHUNKER] Carregando: {caminho}")

    if caminho.endswith(".pdf"):
        loader = TextLoader(caminho, encoding="utf-8")
    else:
        loader = TextLoader(caminho, encoding="utf-8")

    documentos = loader.load()
    print(f"[CHUNKER] {len(documentos)} pagina(s) carregada(s)")
    return documentos

def dividir_em_chunks(documentos):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(documentos)
    print(f"[CHUNKER] {len(chunks)} chunks gerados")
    return chunks

def processar_pasta(pasta: str = None):
    if pasta is None:
        pasta = DATA_RAW

    todos_chunks = []
    arquivos = [f for f in os.listdir(pasta)
                if f.endswith((".txt", ".pdf"))]

    print(f"[CHUNKER] {len(arquivos)} arquivo(s) encontrado(s)")

    for arquivo in arquivos:
        caminho = os.path.join(pasta, arquivo)
        documentos = carregar_documento(caminho)
        chunks     = dividir_em_chunks(documentos)
        todos_chunks.extend(chunks)

    print(f"[CHUNKER] Total: {len(todos_chunks)} chunks")
    return todos_chunks