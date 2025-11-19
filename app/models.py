"""
Modelos de dados do sistema de reservas.
Define as tabelas e relacionamentos do banco de dados.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Sala(Base):
    """
    Modelo que representa uma sala de reunião.
    """
    __tablename__ = "salas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    local = Column(String(100), nullable=False, index=True)
    capacidade = Column(Integer, nullable=True)
    descricao = Column(Text, nullable=True)
    ativa = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento com reservas
    reservas = relationship("Reserva", back_populates="sala", cascade="all, delete-orphan")


class Reserva(Base):
    """
    Modelo que representa uma reserva de sala.
    Inclui validação de conflitos de horário.
    """
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    sala_id = Column(Integer, ForeignKey("salas.id"), nullable=False, index=True)
    responsavel = Column(String(200), nullable=False, index=True)
    data_inicio = Column(DateTime(timezone=True), nullable=False, index=True)
    data_fim = Column(DateTime(timezone=True), nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    
    # Campos relacionados ao café
    cafe_necessario = Column(Boolean, default=False)
    cafe_quantidade = Column(Integer, nullable=True)
    cafe_descricao = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento com sala
    sala = relationship("Sala", back_populates="reservas")


class Usuario(Base):
    """
    Modelo que representa um usuário do sistema.
    Usado para autenticação (opcional).
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

