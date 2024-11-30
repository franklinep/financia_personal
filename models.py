from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
from uuid import uuid4
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError

class Transaccion(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: uuid4().hex, alias="_id")
    monto: float # Positivo para ingresos, negativo para gastos.
    fecha: date
    lugar: Optional[str] = None
    destino: Optional[str] = None # eg tienda alicia, chifa california, etc.
    categoria: Optional[str] = None # eg comida, transporte, luz, agua, etc.
    cajero: Optional[bool] = False # la operacion fue realizada con cajero o no.

class Cuenta(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex, alias="_id")
    tipo: str
    saldo_disponible: float = Field(gt=0)
    nombre: Optional[str] = None
    transacciones: Optional[List[Transaccion]] = Field(default_factory=list)

    @field_validator('tipo')
    def validate_tipo(cls, t):
        if t not in ['Credito', 'Debito', 'Efectivo']:
            raise ValueError('El Tipo tarjeta debe ser Credito, Debito o Efectivo')
        return t
    
    @model_validator(mode='after')
    def actualizar_saldo(cls, values):
        # Si ya hay transacciones, actualizar el saldo
        if 'transacciones' in values and values['transacciones']:
            saldo = values.get('saldo_disponible', 0)
            for transaccion in values['transacciones']:
                saldo += transaccion['monto']
            values['saldo_disponible'] = saldo
        return values

# Nuestro modelo usuario base, el esquema
class Usuario(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex, alias="_id")
    nombre: Optional[str]
    email: Optional[str]
    cuentas: Optional[List[Cuenta]] = Field(default_factory=list)
    fecha_registro: Optional[date] = Field(default_factory=date)
    fecha_de_nacimiento: Optional[date] = Field(default=None)
    lugar_de_residencia: Optional[str] = Field(default=None)

    @field_validator('email')
    def validar_formato(cls, v):
        try:
            valid = validate_email(v)
            return valid.email
        except EmailNotValidError:
            raise ValueError('Correo electrónico inválido')
        
# Las propiedades que debe recibir el API para crear un usuario
class UsuarioCreate(Usuario):
    nombre: str
    cuentas: List[Cuenta]


        

