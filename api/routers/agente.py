from fastapi import APIRouter, HTTPException
from api.schemas import PerguntaRequest, RespostaResponse, MetricasResponse
from src.graphs.main_graph import grafo
from src.utils.dashboard import historico_avaliacoes, registrar_avaliacao

router = APIRouter(prefix="/agente", tags=["Agente RAG"])

# Sessoes em memoria — uma por session_id
sessoes: dict = {}

def get_ou_criar_sessao(session_id: str) -> list:
    if session_id not in sessoes:
        sessoes[session_id] = []
    return sessoes[session_id]

def criar_state(pergunta: str, historico: list) -> dict:
    return {
        "pergunta":     pergunta,
        "rota":         "",
        "contexto":     [],
        "fontes":       [],
        "resposta":     "",
        "tentativas":   0,
        "qualidade_ok": False,
        "erro":         None,
        "historico":    historico.copy(),
        "precisa_rag":  False,
        "precisa_sql":  False,
        "contexto_rag": [],
        "contexto_sql": [],
        "fontes_rag":   [],
        "fontes_sql":   [],
        "metricas":     {},
        "score_geral":  0.0,
    }

@router.post("/perguntar", response_model=RespostaResponse)
async def perguntar(request: PerguntaRequest):
    try:
        historico = get_ou_criar_sessao(request.session_id)
        state     = criar_state(request.pergunta, historico)
        resultado = grafo.invoke(state)

        # Atualiza historico da sessao
        sessoes[request.session_id] = resultado["historico"]

        return RespostaResponse(
            resposta     = resultado["resposta"],
            rota         = resultado["rota"],
            tentativas   = resultado["tentativas"],
            qualidade_ok = resultado["qualidade_ok"],
            score_geral  = resultado.get("score_geral", 0.0),
            fontes       = resultado["fontes"],
            session_id   = request.session_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar pergunta: {str(e)}"
        )

@router.get("/metricas", response_model=MetricasResponse)
async def get_metricas():
    if not historico_avaliacoes:
        return MetricasResponse(
            total_interacoes    = 0,
            score_medio         = 0.0,
            faithfulness_medio  = 0.0,
            relevancia_media    = 0.0,
            precisao_media      = 0.0,
        )

    total = len(historico_avaliacoes)
    return MetricasResponse(
        total_interacoes   = total,
        score_medio        = round(sum(r["score_geral"]  for r in historico_avaliacoes) / total, 2),
        faithfulness_medio = round(sum(r["faithfulness"] for r in historico_avaliacoes) / total, 2),
        relevancia_media   = round(sum(r["relevancia"]   for r in historico_avaliacoes) / total, 2),
        precisao_media     = round(sum(r["precisao"]     for r in historico_avaliacoes) / total, 2),
    )

@router.delete("/sessao/{session_id}")
async def limpar_sessao(session_id: str):
    if session_id in sessoes:
        del sessoes[session_id]
    return {"mensagem": f"Sessao {session_id} limpa com sucesso"}