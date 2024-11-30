from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from bson import ObjectId

from models import Transaccion, Cuenta, Usuario, UsuarioCreate

router = APIRouter()

# CREATE
@router.post("/usuarios/", description="Crear usuario", response_model=UsuarioCreate, status_code=status.HTTP_201_CREATED)
async def crear_usuario(request: Request, usuario: UsuarioCreate = Body(...)) -> Usuario:
    usuario = jsonable_encoder(usuario)
    request.app.database["usuarios"].insert_one(usuario)
    usuario_creado = request.app.database["usuarios"].find_one(
        {"_id": usuario["_id"]}
    )
    return usuario_creado

# READ
@router.get("/usuarios/", description="Listar usuarios", response_model=List[Usuario])
def listar_usuarios(request: Request):
    usuarios = list(request.app.database["usuarios"].find())
    return usuarios

# UPDATE - AÑADIR NUEVA CUENTA AL USUARIO
@router.put("/usuarios/{id}/cuentas", description="Añadir cuenta a Usuario", response_model=Usuario)
def agregar_cuenta_a_usuario(request: Request, id: str, nueva_cuenta: Cuenta = Body(...)):
    nueva_cuenta_json = jsonable_encoder(nueva_cuenta)
    
    resultado = request.app.database["usuarios"].update_one(
        {"_id": id}, 
        {"$push": {"cuentas": nueva_cuenta_json}}
    )
    
    if resultado.modified_count == 1:
        usuario_actualizado = request.app.database["usuarios"].find_one({"_id": id})
        return usuario_actualizado
    else:
        raise HTTPException(status_code=404, detail=f"El usuario con {id} no existe")

# UPDATE - AÑADIR TRANSACCION A UNA CUENTA DEL USUARIO
@router.put("/usuarios/{id}/cuentas/{cuenta_id}/transacciones", description="Añadir transacción a cuenta")
def agregar_transaccion_a_cuenta(request: Request, id: str, cuenta_id: str, nueva_transaccion: Transaccion = Body(...)):
    nueva_transaccion_json = jsonable_encoder(nueva_transaccion)
    
    resultado = request.app.database["usuarios"].update_one(
        {
            "_id": id, 
            "cuentas._id": cuenta_id
        }, 
        {
            "$push": {"cuentas.$.transacciones": nueva_transaccion_json},
            "$inc": {"cuentas.$.saldo_disponible": nueva_transaccion.monto}
        }
    )
     
    if resultado.modified_count == 1:
        usuario_actualizado = request.app.database["usuarios"].find_one({"_id": id})
        return usuario_actualizado
    else:
        raise HTTPException(status_code=404, detail=f"Usuario o cuenta no encontrados")

# DELETE
@router.delete("/usuarios/{id}", description="Eliminar Usuario")
def eliminar_usuario(request: Request, id: str, response: Response):
    usuario_eliminado = request.app.database["usuarios"].delete_one({"_id": id})

    if usuario_eliminado.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    else: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El usuario no existe")