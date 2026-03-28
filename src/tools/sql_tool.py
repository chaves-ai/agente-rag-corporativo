import sqlite3
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from src.config import TEMPERATURA

BANCO = os.path.join("data", "banco_corporativo.db")

modelo = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

SCHEMA = """
Tabela: vendas
Colunas:
  - id         (INTEGER) chave primaria
  - mes        (TEXT)    ex: Janeiro, Fevereiro, Marco
  - ano        (INTEGER) ex: 2024
  - produto    (TEXT)    ex: Software A, Software B, Software C
  - vendedor   (TEXT)    ex: Ana Silva, Carlos Lima
  - estado     (TEXT)    ex: SP, RJ, MG, RS
  - valor      (REAL)    valor da venda em reais
  - quantidade (INTEGER) numero de unidades vendidas

Tabela: colaboradores
Colunas:
  - id           (INTEGER) chave primaria
  - nome         (TEXT)    nome completo
  - cargo        (TEXT)    ex: Vendedor Senior, Analista Junior
  - departamento (TEXT)    ex: Comercial, Marketing, TI
  - salario      (REAL)    salario mensal em reais
  - estado       (TEXT)    ex: SP, RJ, MG, RS
  - data_admissao (TEXT)   formato: YYYY-MM-DD
"""

def gerar_sql(pergunta: str) -> str:
    prompt = f"""Voce e um especialista em SQL.
Converta a pergunta abaixo em uma query SQL valida para SQLite.

SCHEMA DO BANCO:
{SCHEMA}

REGRAS:
- Retorne SOMENTE a query SQL — sem explicacao, sem markdown
- Use apenas as tabelas e colunas do schema acima
- Para valores monetarios use ROUND com 2 casas decimais
- Sempre use ORDER BY quando fizer sentido
- Limite resultados com LIMIT 10 quando nao especificado

PERGUNTA: {pergunta}

SQL:"""

    resposta = modelo.invoke([HumanMessage(content=prompt)])
    sql = resposta.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def executar_sql(sql: str) -> str:
    try:
        # Pega apenas a primeira query se vier mais de uma
        sql = sql.split(";")[0].strip()
        if not sql:
            return "Nenhuma query gerada."

        conn   = sqlite3.connect(BANCO)
        cursor = conn.cursor()

        print(f"[SQL_TOOL] Executando: {sql}")
        cursor.execute(sql)

        colunas    = [desc[0] for desc in cursor.description]
        resultados = cursor.fetchall()
        conn.close()

        if not resultados:
            return "Nenhum resultado encontrado para essa consulta."

        linhas = []
        linhas.append(" | ".join(colunas))
        linhas.append("-" * 50)
        for row in resultados:
            linhas.append(" | ".join(str(v) for v in row))

        return "\n".join(linhas)

    except Exception as e:
        return f"Erro ao executar SQL: {str(e)}"

def consultar(pergunta: str) -> str:
    print(f"[SQL_TOOL] Gerando SQL para: '{pergunta}'")
    sql       = gerar_sql(pergunta)
    print(f"[SQL_TOOL] SQL gerado: {sql}")
    resultado = executar_sql(sql)
    print(f"[SQL_TOOL] Resultado: {resultado[:100]}...")
    return resultado