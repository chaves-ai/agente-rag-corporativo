from datetime import datetime

historico_avaliacoes = []

def registrar_avaliacao(pergunta: str, resposta: str,
                        metricas: dict, rota: str):
    registro = {
        "timestamp":    datetime.now().strftime("%H:%M:%S"),
        "pergunta":     pergunta[:60],
        "rota":         rota,
        "faithfulness": metricas.get("faithfulness", 0),
        "relevancia":   metricas.get("relevancia", 0),
        "precisao":     metricas.get("precisao", 0),
        "score_geral":  metricas.get("score_geral", 0),
    }
    historico_avaliacoes.append(registro)
    return registro

def exibir_dashboard():
    if not historico_avaliacoes:
        print("Nenhuma avaliacao registrada ainda.")
        return

    print("\n" + "="*60)
    print("DASHBOARD DE QUALIDADE DO AGENTE")
    print("="*60)

    total        = len(historico_avaliacoes)
    media_geral  = sum(r["score_geral"]  for r in historico_avaliacoes) / total
    media_faith  = sum(r["faithfulness"] for r in historico_avaliacoes) / total
    media_relev  = sum(r["relevancia"]   for r in historico_avaliacoes) / total
    media_prec   = sum(r["precisao"]     for r in historico_avaliacoes) / total

    print(f"\nRESUMO GERAL ({total} interacoes)")
    print(f"  Score Geral:   {media_geral:.2f} {_barra(media_geral)}")
    print(f"  Faithfulness:  {media_faith:.2f} {_barra(media_faith)}")
    print(f"  Relevancia:    {media_relev:.2f} {_barra(media_relev)}")
    print(f"  Precisao:      {media_prec:.2f} {_barra(media_prec)}")

    print(f"\nHISTORICO DETALHADO")
    print(f"{'Hora':<10} {'Rota':<12} {'Geral':<8} {'Faith':<8} {'Relev':<8} Pergunta")
    print("-"*70)

    for r in historico_avaliacoes[-10:]:
        print(f"{r['timestamp']:<10} {r['rota']:<12} "
              f"{r['score_geral']:<8.2f} {r['faithfulness']:<8.2f} "
              f"{r['relevancia']:<8.2f} {r['pergunta'][:30]}")

    print("="*60 + "\n")

def _barra(score: float) -> str:
    blocos = int(score * 10)
    return "[" + "█" * blocos + "░" * (10 - blocos) + "]"