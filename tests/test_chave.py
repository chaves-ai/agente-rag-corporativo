from src.config import OPENAI_API_KEY

if not OPENAI_API_KEY:
    print("ERRO: OPENAI_API_KEY esta vazia no .env")
elif OPENAI_API_KEY == "sua_chave_aqui":
    print("ERRO: voce nao substituiu a chave no .env")
elif not OPENAI_API_KEY.startswith("sk-"):
    print("ERRO: chave invalida — deve comecar com sk-")
else:
    print("Chave OK:", OPENAI_API_KEY[:8] + "...")