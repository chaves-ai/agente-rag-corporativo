from pydantic import BaseModel
from typing import List, Optional, Dict

class PerguntaRequest(BaseModel):
    pergunta: str
    session_id: Optional[str] = "default"

class RespostaResponse(BaseModel):
    resposta:    str
    rota:        str
    tentativas:  int
    qualidade_ok: bool
    score_geral: float
    fontes:      List[str]
    session_id:  str

class MetricasResponse(BaseModel):
    total_interacoes: int
    score_medio:      float
    faithfulness_medio: float
    relevancia_media: float
    precisao_media:   float

class HealthResponse(BaseModel):
    status:  str
    versao:  str
    agente:  str