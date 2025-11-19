"""
Rotas para gerenciamento de reservas.
Inclui validação de conflitos de horário.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Reserva, Sala
from app.schemas import (
    ReservaCreate,
    ReservaUpdate,
    ReservaResponse,
    ReservaListResponse
)
from app.services import criar_reserva, atualizar_reserva

router = APIRouter(prefix="/api/reservas", tags=["reservas"])


@router.get("/", response_model=List[ReservaListResponse], summary="Listar todas as reservas")
def listar_reservas(
    skip: int = 0,
    limit: int = 100,
    sala_id: Optional[int] = None,
    responsavel: Optional[str] = None,
    data_inicio: Optional[datetime] = Query(None, description="Filtrar reservas a partir desta data"),
    data_fim: Optional[datetime] = Query(None, description="Filtrar reservas até esta data"),
    db: Session = Depends(get_db)
):
    """
    Lista todas as reservas cadastradas com opções de filtro.
    
    - **skip**: Número de registros a pular (para paginação)
    - **limit**: Número máximo de registros a retornar
    - **sala_id**: Filtrar por sala específica (opcional)
    - **responsavel**: Filtrar por responsável (opcional)
    - **data_inicio**: Filtrar reservas a partir desta data (opcional)
    - **data_fim**: Filtrar reservas até esta data (opcional)
    """
    query = db.query(
        Reserva.id,
        Reserva.sala_id,
        Sala.nome.label('sala_nome'),
        Sala.local.label('sala_local'),
        Reserva.responsavel,
        Reserva.data_inicio,
        Reserva.data_fim,
        Reserva.descricao,
        Reserva.cafe_necessario,
        Reserva.cafe_quantidade,
        Reserva.cafe_descricao,
        Reserva.created_at
    ).join(Sala, Reserva.sala_id == Sala.id)
    
    if sala_id:
        query = query.filter(Reserva.sala_id == sala_id)
    if responsavel:
        query = query.filter(Reserva.responsavel.ilike(f"%{responsavel}%"))
    if data_inicio:
        query = query.filter(Reserva.data_inicio >= data_inicio)
    if data_fim:
        query = query.filter(Reserva.data_fim <= data_fim)
    
    reservas = query.order_by(Reserva.data_inicio.desc()).offset(skip).limit(limit).all()
    
    return [
        ReservaListResponse(
            id=r.id,
            sala_id=r.sala_id,
            sala_nome=r.sala_nome,
            sala_local=r.sala_local,
            responsavel=r.responsavel,
            data_inicio=r.data_inicio,
            data_fim=r.data_fim,
            descricao=r.descricao,
            cafe_necessario=r.cafe_necessario,
            cafe_quantidade=r.cafe_quantidade,
            cafe_descricao=r.cafe_descricao,
            created_at=r.created_at
        )
        for r in reservas
    ]


@router.get("/{reserva_id}", response_model=ReservaResponse, summary="Obter reserva por ID")
def obter_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """
    Obtém uma reserva específica pelo ID.
    """
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada"
        )
    return reserva


@router.post("/", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED, summary="Criar nova reserva")
def criar_nova_reserva(reserva: ReservaCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova reserva com validação de conflitos de horário.
    
    Campos obrigatórios:
    - **sala_id**: ID da sala a ser reservada
    - **responsavel**: Nome do responsável pela reserva
    - **data_inicio**: Data e hora de início
    - **data_fim**: Data e hora de término
    
    Campos opcionais:
    - **descricao**: Descrição da reserva
    - **cafe_necessario**: Se é necessário café (padrão: false)
    - **cafe_quantidade**: Quantidade de cafés (se cafe_necessario = true)
    - **cafe_descricao**: Descrição adicional sobre o café
    """
    # Verificar se a sala existe
    sala = db.query(Sala).filter(Sala.id == reserva.sala_id).first()
    if not sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala não encontrada"
        )
    
    if not sala.ativa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A sala não está ativa para reservas"
        )
    
    # Criar reserva (com validação de conflitos)
    return criar_reserva(db=db, reserva=reserva)


@router.put("/{reserva_id}", response_model=ReservaResponse, summary="Atualizar reserva")
def atualizar_nova_reserva(
    reserva_id: int,
    reserva: ReservaUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza uma reserva existente com validação de conflitos de horário.
    """
    # Se estiver atualizando a sala, verificar se existe
    if reserva.sala_id:
        sala = db.query(Sala).filter(Sala.id == reserva.sala_id).first()
        if not sala:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sala não encontrada"
            )
        if not sala.ativa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A sala não está ativa para reservas"
            )
    
    # Atualizar reserva (com validação de conflitos)
    return atualizar_reserva(db=db, reserva_id=reserva_id, reserva_update=reserva)


@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir reserva")
def excluir_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """
    Exclui uma reserva.
    """
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada"
        )
    
    db.delete(reserva)
    db.commit()
    return None


@router.get("/sala/{sala_id}/disponibilidade", summary="Verificar disponibilidade de sala")
def verificar_disponibilidade(
    sala_id: int,
    data_inicio: datetime = Query(..., description="Data/hora de início"),
    data_fim: datetime = Query(..., description="Data/hora de fim"),
    db: Session = Depends(get_db)
):
    """
    Verifica se uma sala está disponível em um determinado horário.
    Retorna True se disponível, False se houver conflito.
    """
    sala = db.query(Sala).filter(Sala.id == sala_id).first()
    if not sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala não encontrada"
        )
    
    if data_fim <= data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data de fim deve ser posterior à data de início"
        )
    
    # Verificar conflitos
    conflito = db.query(Reserva).filter(
        and_(
            Reserva.sala_id == sala_id,
            Reserva.data_inicio < data_fim,
            Reserva.data_fim > data_inicio
        )
    ).first()
    
    return {
        "disponivel": conflito is None,
        "sala_id": sala_id,
        "data_inicio": data_inicio,
        "data_fim": data_fim
    }

