# Protocolos Operacionais — Agente RAG Corporativo

> **chaves-ai** | Versão 1.0 | 2025

Este documento formaliza os protocolos operacionais do Agente RAG Corporativo da chaves-ai.
Cada protocolo define responsabilidades, regras de operação e compromissos de entrega entre a chaves-ai e o cliente.

---

## Índice

| # | Protocolo | Categoria |
|---|-----------|-----------|
| 01 | [Entrega de Documentos](#protocolo-01--entrega-de-documentos) | Operacional |
| 02 | [Qualidade de Respostas](#protocolo-02--qualidade-de-respostas) | Qualidade |
| 03 | [Segurança e Acesso](#protocolo-03--segurança-e-acesso) | Segurança |
| 04 | [Indexação de Documentos](#protocolo-04--indexação-de-documentos) | Operacional |
| 05 | [Monitoramento](#protocolo-05--monitoramento-e-observabilidade) | Observabilidade |
| 06 | [Versionamento de Código](#protocolo-06--versionamento-de-código) | Engenharia |
| 07 | [Manutenção e Suporte](#protocolo-07--manutenção-e-suporte) | Operacional |
| 08 | [Escalabilidade](#protocolo-08--escalabilidade-e-evolução) | Arquitetura |

---

## PROTOCOLO 01 — Entrega de Documentos

### Princípio Fundamental

> **"O cliente entrega documentos prontos. O agente lê e responde."**
>
> A responsabilidade do agente é processar e responder com base nos documentos fornecidos — não transformar, corrigir ou recalcular os documentos.

### Responsabilidades

| Parte | Responsabilidade |
|-------|-----------------|
| **Cliente** | Entregar documentos finalizados, revisados e salvos em seu aplicativo nativo (Excel, Word, etc.) |
| **chaves-ai** | Indexar os documentos recebidos e garantir que o agente responda com base neles |
| **Agente** | Ler os documentos indexados e gerar respostas fundamentadas no conteúdo fornecido |

### Formatos Suportados

| Formato | Requisito de Entrega |
|---------|---------------------|
| `.xlsx` / `.xls` | Abrir no Excel e salvar antes de entregar — garante que fórmulas estejam calculadas |
| `.pdf` | PDF com texto selecionável — PDFs escaneados sem OCR não são suportados |
| `.docx` | Documento Word finalizado e salvo |
| `.txt` | Arquivo de texto plano em codificação UTF-8 |
| `.csv` | CSV com cabeçalho na primeira linha e codificação UTF-8 |

### Regras Operacionais

- Documentos com fórmulas não calculadas gerarão respostas incorretas — responsabilidade do cliente garantir o cálculo antes da entrega.
- PDFs escaneados sem OCR não são processáveis — o cliente deve garantir que o texto seja selecionável.
- Documentos xlsx com múltiplas abas devem ter cada aba nomeada de forma descritiva (ex: `Janeiro`, `Fevereiro`) — abas com nomes genéricos como `Planilha1` comprometem a precisão.
- O agente **não modifica, corrige ou transforma** nenhum documento entregue.

---

## PROTOCOLO 02 — Qualidade de Respostas

### Sistema de Validação em 3 Níveis

Toda resposta gerada pelo agente passa por validação automática antes de ser entregue ao usuário.

| Nível | Condição | Resultado |
|-------|----------|-----------|
| **Nível 1 — Ausência** | Agente sinalizou que a informação não existe nos documentos | APROVADO · Score 1.0 · 1 tentativa |
| **Nível 2 — Parcial** | Agente respondeu parte da pergunta e admitiu limitação para o restante | APROVADO · Score 0.7 · 1 tentativa |
| **Nível 3 — LLM** | Avaliação completa por modelo de linguagem | APROVADO se Score ≥ 0.4 · Máx 3 tentativas |

### Métricas de Avaliação

| Métrica | Peso | O que mede |
|---------|------|------------|
| Faithfulness | 40% | A resposta é fiel ao conteúdo dos documentos fornecidos? |
| Relevância | 40% | A resposta responde diretamente à pergunta do usuário? |
| Precisão | 20% | Os documentos recuperados eram relevantes para a pergunta? |
| **Score Geral** | 100% | Média ponderada — mínimo 0.4 para aprovação |

> **Garantia central:** O agente nunca inventa informações. Se a resposta não puder ser fundamentada nos documentos fornecidos, o agente declara explicitamente a ausência da informação.

---

## PROTOCOLO 03 — Segurança e Acesso

### Autenticação

Toda requisição ao agente requer autenticação por API Key no header HTTP.

```
X-API-Key: {chave_do_cliente}
```

| Mecanismo | Especificação |
|-----------|--------------|
| Isolamento | Cada cliente recebe uma API Key única e exclusiva |
| Revogação | Chaves podem ser revogadas sem downtime do sistema |
| Sem exposição | Chaves nunca são armazenadas em código-fonte ou repositório público |
| HTTPS | Em produção toda comunicação é criptografada via TLS/SSL |

### Dados do Cliente

- Os documentos do cliente são armazenados em ambiente isolado — sem acesso por outros clientes.
- O vector store (banco vetorial) é exclusivo por cliente em ambientes multi-tenant.
- Nenhum dado do cliente é utilizado para treinar ou ajustar modelos de linguagem.
- Logs de consultas são mantidos apenas para fins de monitoramento operacional e auditoria.

---

## PROTOCOLO 04 — Indexação de Documentos

### Processo de Indexação

| Etapa | Ação |
|-------|------|
| 1. Limpeza | A collection existente é limpa antes de cada reindexação — elimina duplicatas e conteúdo desatualizado |
| 2. Leitura | Todos os documentos da pasta de dados são lidos e convertidos em texto |
| 3. Chunking | Documentos são divididos em chunks de 500 caracteres com sobreposição de 50 |
| 4. Embedding | Cada chunk é convertido em vetor de 384 dimensões pelo modelo fastembed local |
| 5. Persistência | Chunks e vetores são armazenados no ChromaDB — persiste entre reinicializações |

> A reindexação é atômica — ou processa todos os documentos com sucesso, ou mantém o estado anterior intacto.

---

## PROTOCOLO 05 — Monitoramento e Observabilidade

### Stack de Monitoramento

| Ferramenta | O que monitora |
|-----------|----------------|
| LangSmith | Rastreamento completo de cada consulta — nodes, tempo por etapa, tokens, scores |
| FastAPI Logs | Registro de todas as requisições HTTP — status, tempo, erros |
| `/health` | Endpoint de saúde para verificação de disponibilidade |
| `/agente/metricas` | Scores médios agregados de qualidade |

### SLA

- Score médio abaixo de 0.6 por mais de 10 consultas consecutivas dispara revisão dos documentos.
- Tempo de resposta esperado: **3 a 8 segundos** por consulta em condições normais.
- Disponibilidade alvo: **99%** em ambiente de produção com restart automático.

---

## PROTOCOLO 06 — Versionamento de Código

### Padrão de Commits — Conventional Commits

| Prefixo | Quando usar |
|---------|------------|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `refactor:` | Melhoria sem mudança de comportamento externo |
| `docs:` | Documentação |
| `chore:` | Manutenção e dependências |

**Regra:** Cada commit tem uma única responsabilidade e mensagem precisa. Commits com múltiplas responsabilidades são proibidos.

---

## PROTOCOLO 07 — Manutenção e Suporte

### Ciclo de Manutenção

| Atividade | Frequência | Responsável |
|-----------|-----------|-------------|
| Atualização de documentos | Sob demanda do cliente | Cliente + chaves-ai |
| Reindexação | A cada atualização de documentos | chaves-ai |
| Revisão de scores de qualidade | Semanal | chaves-ai |
| Atualização de dependências | Trimestral | chaves-ai |
| Backup do vector store | Semanal | chaves-ai |

### Procedimento de Atualização de Documentos

1. Cliente prepara os documentos atualizados em seus aplicativos nativos.
2. Cliente entrega os documentos via canal acordado em contrato.
3. chaves-ai valida formato e legibilidade dos documentos.
4. chaves-ai executa reindexação e confirma chunks indexados.
5. chaves-ai realiza teste com queries de referência definidas pelo cliente.
6. Sistema disponibilizado com os novos documentos.

---

## PROTOCOLO 08 — Escalabilidade e Evolução

### Modelo de Evolução por Demanda

| Fase | Gatilho | Evolução |
|------|---------|---------|
| **Fase 1** (Atual) | Primeiro cliente | Sistema local ou VPS — um cliente por instância |
| **Fase 2** | 2 a 5 clientes | Interface de upload para autonomia do cliente |
| **Fase 3** | 5+ clientes | Multi-tenancy — isolamento entre clientes |
| **Fase 4** | Demanda por dados estruturados | SQL Node — integração com banco de dados |
| **Fase 5** | Alto volume de consultas | Cache Redis, balanceamento de carga |

> A arquitetura atual suporta as fases 1 e 2 sem modificações estruturais. As fases 3 a 5 são implementadas sob contrato específico quando a demanda justificar. **Nenhuma fase é cobrada antecipadamente.**

---

## Vigência e Revisão

Este documento entra em vigor na data de assinatura do contrato de prestação de serviços.
Os protocolos são revisados anualmente ou sempre que houver mudança significativa na arquitetura.

---

*chaves-ai | Wagno Chaves | wagno@chaves-ai.dev | github.com/chaves-ai/agente-rag-corporativo*
