from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from src.config import TEMPERATURA
import json

modelo = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

def avaliar_faithfulness(pergunta: str, contexto: list, resposta: str) -> float:
    if not contexto:
        return 0.5

    contexto_texto = "\n".join(contexto[:3])

    prompt = f"""Avalie se a resposta e fiel ao contexto fornecido.

CONTEXTO:
{contexto_texto}

PERGUNTA: {pergunta}
RESPOSTA: {resposta}

Criterios:
- 1.0: resposta baseada totalmente no contexto
- 0.7: resposta majoritariamente no contexto
- 0.5: resposta parcialmente no contexto
- 0.2: resposta pouco relacionada ao contexto
- 0.0: resposta inventada sem base no contexto

Responda APENAS com um numero decimal entre 0 e 1.
SCORE:"""

    try:
        resultado = modelo.invoke([HumanMessage(content=prompt)])
        score     = float(resultado.content.strip())
        return round(min(max(score, 0.0), 1.0), 2)
    except:
        return 0.5

def avaliar_relevancia(pergunta: str, resposta: str) -> float:
    prompt = f"""Avalie se a resposta e relevante para a pergunta.

PERGUNTA: {pergunta}
RESPOSTA: {resposta}

Criterios:
- 1.0: resposta responde diretamente a pergunta
- 0.7: resposta relacionada mas nao totalmente direta
- 0.5: resposta parcialmente relevante
- 0.2: resposta pouco relacionada a pergunta
- 0.0: resposta nao tem relacao com a pergunta

Responda APENAS com um numero decimal entre 0 e 1.
SCORE:"""

    try:
        resultado = modelo.invoke([HumanMessage(content=prompt)])
        score     = float(resultado.content.strip())
        return round(min(max(score, 0.0), 1.0), 2)
    except:
        return 0.5

def avaliar_contexto(pergunta: str, contexto: list) -> float:
    if not contexto:
        return 0.0

    contexto_texto = "\n".join(contexto[:3])

    prompt = f"""Avalie se o contexto recuperado e relevante para responder a pergunta.

PERGUNTA: {pergunta}

CONTEXTO RECUPERADO:
{contexto_texto}

Criterios:
- 1.0: contexto perfeitamente relevante
- 0.7: contexto majoritariamente relevante
- 0.5: contexto parcialmente relevante
- 0.2: contexto pouco relevante
- 0.0: contexto irrelevante para a pergunta

Responda APENAS com um numero decimal entre 0 e 1.
SCORE:"""

    try:
        resultado = modelo.invoke([HumanMessage(content=prompt)])
        score     = float(resultado.content.strip())
        return round(min(max(score, 0.0), 1.0), 2)
    except:
        return 0.5

def avaliar_completo(pergunta: str, contexto: list,
                     resposta: str) -> dict:
    print(f"[AVALIADOR] Avaliando qualidade...")

    faithfulness = avaliar_faithfulness(pergunta, contexto, resposta)
    relevancia   = avaliar_relevancia(pergunta, resposta)
    precisao     = avaliar_contexto(pergunta, contexto)

    # Media ponderada
    score_geral = round(
        (faithfulness * 0.4 +
         relevancia   * 0.4 +
         precisao     * 0.2), 2
    )

    metricas = {
        "faithfulness": faithfulness,
        "relevancia":   relevancia,
        "precisao":     precisao,
        "score_geral":  score_geral,
    }

    print(f"[AVALIADOR] Faithfulness: {faithfulness}")
    print(f"[AVALIADOR] Relevancia:   {relevancia}")
    print(f"[AVALIADOR] Precisao:     {precisao}")
    print(f"[AVALIADOR] Score geral:  {score_geral}")

    return metricas