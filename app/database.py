"""
Módulo de configuração do banco de dados.
Utiliza SQLAlchemy para gerenciar conexões e sessões.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# URL de conexão com o banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/reservas_db")

# Criação do engine do SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Criação da sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obter sessão do banco de dados.
    Usado pelo FastAPI para injetar a sessão nas rotas.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

