from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import agente

app = FastAPI(
    title="Agente RAG Corporativo",
    description="API de IA para consulta de documentos e dados corporativos",
    version="1.0.0",
)

# CORS — permite chamadas de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os routers
app.include_router(agente.router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "status":  "online",
        "versao":  "1.0.0",
        "agente":  "RAG Corporativo",
        "docs":    "/docs",
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}