"""
Rotas para gerenciamento de salas.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Sala
from app.schemas import SalaCreate, SalaUpdate, SalaResponse

router = APIRouter(prefix="/api/salas", tags=["salas"])


@router.get("/", response_model=List[SalaResponse], summary="Listar todas as salas")
def listar_salas(
    skip: int = 0,
    limit: int = 100,
    ativa: bool = None,
    db: Session = Depends(get_db)
):
    """
    Lista todas as salas cadastradas.
    
    - **skip**: Número de registros a pular (para paginação)
    - **limit**: Número máximo de registros a retornar
    - **ativa**: Filtrar por salas ativas/inativas (opcional)
    """
    query = db.query(Sala)
    if ativa is not None:
        query = query.filter(Sala.ativa == ativa)
    salas = query.offset(skip).limit(limit).all()
    return salas


@router.get("/{sala_id}", response_model=SalaResponse, summary="Obter sala por ID")
def obter_sala(sala_id: int, db: Session = Depends(get_db)):
    """
    Obtém uma sala específica pelo ID.
    """
    sala = db.query(Sala).filter(Sala.id == sala_id).first()
    if not sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala não encontrada"
        )
    return sala


@router.post("/", response_model=SalaResponse, status_code=status.HTTP_201_CREATED, summary="Criar nova sala")
def criar_sala(sala: SalaCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova sala.
    
    - **nome**: Nome da sala (único)
    - **local**: Local onde a sala está localizada
    - **capacidade**: Capacidade máxima (opcional)
    - **descricao**: Descrição adicional (opcional)
    """
    # Verificar se já existe sala com mesmo nome
    sala_existente = db.query(Sala).filter(Sala.nome == sala.nome).first()
    if sala_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma sala com este nome"
        )
    
    db_sala = Sala(**sala.dict())
    db.add(db_sala)
    db.commit()
    db.refresh(db_sala)
    return db_sala


@router.put("/{sala_id}", response_model=SalaResponse, summary="Atualizar sala")
def atualizar_sala(sala_id: int, sala: SalaUpdate, db: Session = Depends(get_db)):
    """
    Atualiza uma sala existente.
    """
    db_sala = db.query(Sala).filter(Sala.id == sala_id).first()
    if not db_sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala não encontrada"
        )
    
    # Verificar se o novo nome já existe (se estiver atualizando o nome)
    if sala.nome and sala.nome != db_sala.nome:
        sala_existente = db.query(Sala).filter(Sala.nome == sala.nome).first()
        if sala_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma sala com este nome"
            )
    
    # Atualizar campos
    update_data = sala.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_sala, field, value)
    
    db.commit()
    db.refresh(db_sala)
    return db_sala


@router.delete("/{sala_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir sala")
def excluir_sala(sala_id: int, db: Session = Depends(get_db)):
    """
    Exclui uma sala.
    Note: Reservas associadas serão excluídas em cascata.
    """
    db_sala = db.query(Sala).filter(Sala.id == sala_id).first()
    if not db_sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala não encontrada"
        )
    
    db.delete(db_sala)
    db.commit()
    return None

