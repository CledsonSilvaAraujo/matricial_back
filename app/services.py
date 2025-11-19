"""
Serviços de negócio do sistema.
Contém a lógica de validação de conflitos de horário.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models import Reserva
from app.schemas import ReservaCreate, ReservaUpdate
from fastapi import HTTPException, status


def verificar_conflito_horario(
    db: Session,
    sala_id: int,
    data_inicio: datetime,
    data_fim: datetime,
    reserva_id_excluir: int = None
) -> bool:
    """
    Verifica se existe conflito de horário para uma reserva.
    
    Args:
        db: Sessão do banco de dados
        sala_id: ID da sala a ser verificada
        data_inicio: Data/hora de início da reserva
        data_fim: Data/hora de fim da reserva
        reserva_id_excluir: ID da reserva a ser excluída da verificação (para updates)
    
    Returns:
        True se há conflito, False caso contrário
    """
    # Query para encontrar reservas conflitantes
    # Conflito ocorre quando:
    # 1. Nova reserva começa durante uma reserva existente
    # 2. Nova reserva termina durante uma reserva existente
    # 3. Nova reserva engloba uma reserva existente
    # 4. Nova reserva é englobada por uma reserva existente
    
    query = db.query(Reserva).filter(
        and_(
            Reserva.sala_id == sala_id,
            or_(
                # Caso 1 e 2: Sobreposição parcial
                and_(
                    Reserva.data_inicio < data_fim,
                    Reserva.data_fim > data_inicio
                )
            )
        )
    )
    
    # Excluir a própria reserva se estiver atualizando
    if reserva_id_excluir:
        query = query.filter(Reserva.id != reserva_id_excluir)
    
    conflito = query.first()
    return conflito is not None


def criar_reserva(db: Session, reserva: ReservaCreate) -> Reserva:
    """
    Cria uma nova reserva com validação de conflitos.
    
    Args:
        db: Sessão do banco de dados
        reserva: Dados da reserva a ser criada
    
    Returns:
        Objeto Reserva criado
    
    Raises:
        HTTPException: Se houver conflito de horário
    """
    # Verificar conflito de horário
    if verificar_conflito_horario(
        db=db,
        sala_id=reserva.sala_id,
        data_inicio=reserva.data_inicio,
        data_fim=reserva.data_fim
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma reserva para esta sala no horário especificado"
        )
    
    # Criar reserva
    db_reserva = Reserva(**reserva.dict())
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva


def atualizar_reserva(
    db: Session,
    reserva_id: int,
    reserva_update: ReservaUpdate
) -> Reserva:
    """
    Atualiza uma reserva existente com validação de conflitos.
    
    Args:
        db: Sessão do banco de dados
        reserva_id: ID da reserva a ser atualizada
        reserva_update: Dados atualizados da reserva
    
    Returns:
        Objeto Reserva atualizado
    
    Raises:
        HTTPException: Se a reserva não existir ou houver conflito
    """
    db_reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not db_reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada"
        )
    
    # Preparar dados para atualização
    update_data = reserva_update.dict(exclude_unset=True)
    
    # Se estiver atualizando datas ou sala, verificar conflitos
    if 'data_inicio' in update_data or 'data_fim' in update_data or 'sala_id' in update_data:
        data_inicio = update_data.get('data_inicio', db_reserva.data_inicio)
        data_fim = update_data.get('data_fim', db_reserva.data_fim)
        sala_id = update_data.get('sala_id', db_reserva.sala_id)
        
        if verificar_conflito_horario(
            db=db,
            sala_id=sala_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            reserva_id_excluir=reserva_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma reserva para esta sala no horário especificado"
            )
    
    # Atualizar campos
    for field, value in update_data.items():
        setattr(db_reserva, field, value)
    
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

