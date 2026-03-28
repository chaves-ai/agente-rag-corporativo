import sqlite3
import os

caminho = os.path.join("data", "banco_corporativo.db")
conn = sqlite3.connect(caminho)

conn.execute("UPDATE vendas SET mes='Março' WHERE mes='Marco'")
conn.commit()

meses = conn.execute("SELECT DISTINCT mes FROM vendas").fetchall()
print("Meses no banco:", meses)
conn.close()
print("Banco atualizado com sucesso!")