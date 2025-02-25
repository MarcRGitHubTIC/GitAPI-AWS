from pydantic import BaseModel
from typing import Optional

class Pokemon(BaseModel):
    numero_pokedex: int
    imagen: str
    nombre: str
    tipo1: str
    tipo2: Optional[str] = None

class PokemonUpdate(BaseModel):
    imagen: Optional[str] = None
    nombre: Optional[str] = None
    tipo1: Optional[str] = None
    tipo2: Optional[str] = None
