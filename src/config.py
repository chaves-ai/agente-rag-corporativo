import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY   = os.getenv('GROQ_API_KEY')
MODELO_LLM     = os.getenv('MODELO_LLM', 'gpt-4o-mini')
TEMPERATURA    = float(os.getenv('TEMPERATURA', '0'))
API_KEY        = os.getenv('API_KEY', 'chaves-ai-key-2025')

# ── CAMINHOS ─────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.dirname(__file__))
DATA_RAW       = os.path.join(BASE_DIR, 'data', 'raw')
DATA_PROCESSED = os.path.join(BASE_DIR, 'data', 'processed')
VECTOR_STORE   = os.path.join(BASE_DIR, 'data', 'vector_store')

# ── RAG ──────────────────────────────────────────────
CHUNK_SIZE     = 500
CHUNK_OVERLAP  = 50
TOP_K_RESULTS  = 5

# ── LANGSMITH ────────────────────────────────────────
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2', 'false')
LANGCHAIN_API_KEY    = os.getenv('LANGCHAIN_API_KEY')
LANGCHAIN_PROJECT    = os.getenv('LANGCHAIN_PROJECT', 'agente-rag-corporativo')
LANGCHAIN_ENDPOINT   = os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')

# Ativa o tracing automaticamente ao importar o config
if LANGCHAIN_TRACING_V2 == 'true' and LANGCHAIN_API_KEY:
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_API_KEY']    = LANGCHAIN_API_KEY
    os.environ['LANGCHAIN_PROJECT']    = LANGCHAIN_PROJECT
    os.environ['LANGCHAIN_ENDPOINT']   = LANGCHAIN_ENDPOINT
    print(f"[LANGSMITH] Tracing ativo — projeto: {LANGCHAIN_PROJECT}")
else:
    print("[LANGSMITH] Tracing desativado")