"""
Rotas de autenticação.
Implementa login e registro de usuários.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioResponse, Token
from app.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/auth", tags=["autenticacao"])


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, summary="Registrar novo usuário")
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário no sistema.
    
    - **email**: Email do usuário (deve ser único)
    - **nome**: Nome completo do usuário
    - **senha**: Senha (mínimo 6 caracteres)
    """
    # Verificar se o email já existe
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Criar novo usuário
    db_usuario = Usuario(
        email=usuario.email,
        nome=usuario.nome,
        senha_hash=get_password_hash(usuario.senha)
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


@router.post("/login", response_model=Token, summary="Fazer login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica um usuário e retorna um token JWT.
    
    - **username**: Email do usuário
    - **password**: Senha do usuário
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UsuarioResponse, summary="Obter usuário atual")
def obter_usuario_atual(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna informações do usuário autenticado.
    """
    return current_user

