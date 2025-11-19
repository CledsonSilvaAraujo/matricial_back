"""
Aplicação principal FastAPI.
Configuração de CORS, rotas e middleware.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import salas, reservas, auth
from app.database import engine, Base

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Reserva de Salas",
    description="API RESTful para gerenciamento de reservas de salas de reunião",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(salas.router)
app.include_router(reservas.router)
app.include_router(auth.router)


@app.get("/", tags=["root"])
def root():
    """
    Endpoint raiz da API.
    """
    return {
        "message": "Sistema de Reserva de Salas API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/api/health", tags=["health"])
def health_check():
    """
    Endpoint de verificação de saúde da API.
    """
    return {"status": "healthy"}

