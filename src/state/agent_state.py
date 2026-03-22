from typing import TypedDict, List, Optional, Dict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    pergunta:          str
    rota:              str
    contexto:          List[str]
    fontes:            List[str]
    resposta:          str
    tentativas:        int
    qualidade_ok:      bool
    erro:              Optional[str]
    historico:         List[BaseMessage]
    precisa_rag:       bool
    precisa_sql:       bool
    contexto_rag:      List[str]
    contexto_sql:      List[str]
    fontes_rag:        List[str]
    fontes_sql:        List[str]
    # Campos novos para avaliacao
    metricas:          Dict[str, float]
    score_geral:       float