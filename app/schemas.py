"""
Schemas Pydantic para validação e serialização de dados.
Define os modelos de entrada e saída da API.
"""
from pydantic import BaseModel, EmailStr, Field, model_validator
from datetime import datetime
from typing import Optional, List


# Schemas de Sala
class SalaBase(BaseModel):
    """Schema base para Sala."""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da sala")
    local: str = Field(..., min_length=1, max_length=100, description="Local onde a sala está localizada")
    capacidade: Optional[int] = Field(None, ge=1, description="Capacidade máxima de pessoas")
    descricao: Optional[str] = Field(None, description="Descrição adicional da sala")
    ativa: bool = Field(True, description="Se a sala está ativa para reservas")


class SalaCreate(SalaBase):
    """Schema para criação de sala."""
    pass


class SalaUpdate(BaseModel):
    """Schema para atualização de sala."""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    local: Optional[str] = Field(None, min_length=1, max_length=100)
    capacidade: Optional[int] = Field(None, ge=1)
    descricao: Optional[str] = None
    ativa: Optional[bool] = None


class SalaResponse(SalaBase):
    """Schema de resposta para Sala."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Schemas de Reserva
class ReservaBase(BaseModel):
    """Schema base para Reserva."""
    sala_id: int = Field(..., description="ID da sala a ser reservada")
    responsavel: str = Field(..., min_length=1, max_length=200, description="Nome do responsável pela reserva")
    data_inicio: datetime = Field(..., description="Data e hora de início da reserva")
    data_fim: datetime = Field(..., description="Data e hora de término da reserva")
    descricao: Optional[str] = Field(None, description="Descrição da reserva")
    cafe_necessario: bool = Field(False, description="Se é necessário café")
    cafe_quantidade: Optional[int] = Field(None, ge=1, description="Quantidade de cafés necessários")
    cafe_descricao: Optional[str] = Field(None, description="Descrição adicional sobre o café")

    @model_validator(mode='after')
    def data_fim_deve_ser_posterior_inicio(self):
        """Valida que a data de fim é posterior à data de início."""
        if self.data_fim <= self.data_inicio:
            raise ValueError('A data de fim deve ser posterior à data de início')
        return self


class ReservaCreate(ReservaBase):
    """Schema para criação de reserva."""
    pass


class ReservaUpdate(BaseModel):
    """Schema para atualização de reserva."""
    sala_id: Optional[int] = None
    responsavel: Optional[str] = Field(None, min_length=1, max_length=200)
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    descricao: Optional[str] = None
    cafe_necessario: Optional[bool] = None
    cafe_quantidade: Optional[int] = Field(None, ge=1)
    cafe_descricao: Optional[str] = None


class ReservaResponse(ReservaBase):
    """Schema de resposta para Reserva."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    sala: SalaResponse

    class Config:
        from_attributes = True


class ReservaListResponse(BaseModel):
    """Schema para listagem de reservas."""
    id: int
    sala_id: int
    sala_nome: str
    sala_local: str
    responsavel: str
    data_inicio: datetime
    data_fim: datetime
    descricao: Optional[str]
    cafe_necessario: bool
    cafe_quantidade: Optional[int]
    cafe_descricao: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Schemas de Usuário (para autenticação)
class UsuarioBase(BaseModel):
    """Schema base para Usuário."""
    email: EmailStr
    nome: str = Field(..., min_length=1, max_length=200)


class UsuarioCreate(UsuarioBase):
    """Schema para criação de usuário."""
    senha: str = Field(..., min_length=6, description="Senha do usuário (mínimo 6 caracteres)")


class UsuarioResponse(UsuarioBase):
    """Schema de resposta para Usuário."""
    id: int
    ativo: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Schemas de Autenticação
class Token(BaseModel):
    """Schema para token de autenticação."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema para dados do token."""
    email: Optional[str] = None

