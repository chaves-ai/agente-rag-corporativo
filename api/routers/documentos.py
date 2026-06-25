from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from collections import Counter
from api.schemas import (
    DocumentoResponse,
    ListaDocumentosResponse,
    RemocaoResponse,
)
from src.rag.embeddings import get_ou_criar_collection
from src.config import API_KEY
import secrets
import os

router = APIRouter(prefix="/documentos", tags=["Documentos"])

# ── AUTENTICAÇÃO ─────────────────────────────────────────
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verificar_api_key(api_key: str = Security(api_key_header)):
    if not api_key or not secrets.compare_digest(api_key, API_KEY):
        raise HTTPException(
            status_code=401,
            detail="API key inválida ou ausente."
        )
    return api_key


# ── HELPERS ──────────────────────────────────────────────
def _extrair_nome_arquivo(caminho: str) -> str:
    """Recebe um caminho e retorna apenas o nome do arquivo."""
    return os.path.basename(caminho) if caminho else "desconhecido"


# ── ENDPOINTS ────────────────────────────────────────────
@router.get("/", response_model=ListaDocumentosResponse)
async def listar_documentos(api_key: str = Security(verificar_api_key)):
    """Lista todos os documentos indexados no ChromaDB."""
    try:
        colecao, _ = get_ou_criar_collection()
        dados = colecao.get(include=["metadatas"])
        metadatas = dados.get("metadatas", []) or []

        # Agrupa chunks por nome do arquivo (campo 'source')
        contador = Counter()
        for meta in metadatas:
            source = meta.get("source", "") if meta else ""
            nome = _extrair_nome_arquivo(source)
            contador[nome] += 1

        documentos = [
            DocumentoResponse(nome=nome, chunks=qtd)
            for nome, qtd in sorted(contador.items())
        ]

        return ListaDocumentosResponse(
            total_documentos=len(documentos),
            total_chunks=sum(contador.values()),
            documentos=documentos,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar documentos: {str(e)}"
        )


@router.delete("/{nome}", response_model=RemocaoResponse)
async def remover_documento(nome: str, api_key: str = Security(verificar_api_key)):
    """Remove todos os chunks de um documento específico do índice."""
    try:
        colecao, _ = get_ou_criar_collection()
        dados = colecao.get(include=["metadatas"])
        ids = dados.get("ids", []) or []
        metadatas = dados.get("metadatas", []) or []

        # Coleta os IDs dos chunks que pertencem ao documento
        ids_para_remover = [
            chunk_id
            for chunk_id, meta in zip(ids, metadatas)
            if meta and _extrair_nome_arquivo(meta.get("source", "")) == nome
        ]

        if not ids_para_remover:
            raise HTTPException(
                status_code=404,
                detail=f"Documento '{nome}' não encontrado no índice."
            )

        colecao.delete(ids=ids_para_remover)

        return RemocaoResponse(
            mensagem=f"Documento '{nome}' removido com sucesso.",
            documento=nome,
            chunks_removidos=len(ids_para_remover),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao remover documento: {str(e)}"
        )