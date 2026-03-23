from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, DATA_RAW
import os

# ── FORMATOS SUPORTADOS ──────────────────────────────────
FORMATOS_SUPORTADOS = (".txt", ".pdf", ".docx", ".xlsx", ".csv")

def carregar_txt(caminho: str):
    loader = TextLoader(caminho, encoding="utf-8")
    return loader.load()

def carregar_pdf(caminho: str):
    loader = PyPDFLoader(caminho)
    return loader.load()

def carregar_docx(caminho: str):
    from docx import Document as DocxDocument
    doc = DocxDocument(caminho)
    texto = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    return [Document(page_content=texto, metadata={"source": caminho})]

def carregar_xlsx(caminho: str):
    import openpyxl
    wb = openpyxl.load_workbook(caminho)
    documentos = []
    for nome_aba in wb.sheetnames:
        aba = wb[nome_aba]
        linhas = []
        cabecalho = None
        for i, row in enumerate(aba.iter_rows(values_only=True)):
            row_limpa = [str(c) if c is not None else "" for c in row]
            if i == 0:
                cabecalho = " | ".join(row_limpa)
                linhas.append(f"COLUNAS: {cabecalho}")
            else:
                if any(c for c in row_limpa):
                    linhas.append(" | ".join(row_limpa))
        texto = f"Planilha: {nome_aba}\n" + "\n".join(linhas)
        documentos.append(Document(
            page_content=texto,
            metadata={"source": caminho, "sheet": nome_aba}
        ))
    return documentos

def carregar_csv(caminho: str):
    import pandas as pd
    df = None
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            df_temp = pd.read_csv(caminho, encoding=enc)
            if not df_temp.empty:
                df = df_temp
                break
        except Exception:
            continue
    if df is None:
        raise ValueError(f"Nao foi possivel ler o CSV: {caminho}")
    linhas = []
    cabecalho = " | ".join(df.columns.tolist())
    linhas.append(f"COLUNAS: {cabecalho}")
    for _, row in df.iterrows():
        linhas.append(" | ".join([str(v) for v in row.values]))
    texto = "\n".join(linhas)
    return [Document(page_content=texto, metadata={"source": caminho})]

def carregar_documento(caminho: str):
    print(f"[CHUNKER] Carregando: {caminho}")
    ext = os.path.splitext(caminho)[1].lower()

    loaders = {
        ".txt":  carregar_txt,
        ".pdf":  carregar_pdf,
        ".docx": carregar_docx,
        ".xlsx": carregar_xlsx,
        ".csv":  carregar_csv,
    }

    if ext not in loaders:
        print(f"[CHUNKER] Formato nao suportado: {ext} — ignorando")
        return []

    documentos = loaders[ext](caminho)
    print(f"[CHUNKER] {len(documentos)} pagina(s)/aba(s) carregada(s)")
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
                if f.lower().endswith(FORMATOS_SUPORTADOS)]

    print(f"[CHUNKER] {len(arquivos)} arquivo(s) encontrado(s)")
    print(f"[CHUNKER] Formatos suportados: {', '.join(FORMATOS_SUPORTADOS)}")

    for arquivo in arquivos:
        caminho = os.path.join(pasta, arquivo)
        try:
            documentos = carregar_documento(caminho)
            if documentos:
                chunks = dividir_em_chunks(documentos)
                todos_chunks.extend(chunks)
        except Exception as e:
            print(f"[CHUNKER] ERRO ao processar {arquivo}: {e}")
            continue

    print(f"[CHUNKER] Total: {len(todos_chunks)} chunks")
    return todos_chunks