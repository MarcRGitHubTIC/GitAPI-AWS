from fastapi import FastAPI, HTTPException
from db import get_db_connection
from models import Pokemon, PokemonUpdate
from typing import Optional, List

DELAY_TIME=3

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API PokeAPI en AWS"}

# Obtener todos los Pokémon
@app.get("/pokemons", response_model=List[Pokemon])
def get_pokemons():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pokemon")
    pokemons = cursor.fetchall()
    cursor.close()
    connection.close()
    return pokemons

# Obtener un Pokémon por su número de Pokédex
@app.get("/pokemons/{numero_pokedex}", response_model=Pokemon)
def get_pokemon(numero_pokedex: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pokemon WHERE numero_pokedex = %s", (numero_pokedex,))
    pokemon = cursor.fetchone()
    cursor.close()
    connection.close()
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon no encontrado")
    return pokemon

# Agregar un nuevo Pokémon
@app.post("/pokemons", response_model=Pokemon)
def create_pokemon(pokemon: Pokemon):
    connection = get_db_connection()
    cursor = connection.cursor()
    sql = "INSERT INTO pokemon (numero_pokedex, imagen, nombre, tipo1, tipo2) VALUES (%s, %s, %s, %s, %s)"
    values = (pokemon.numero_pokedex, pokemon.imagen, pokemon.nombre, pokemon.tipo1, pokemon.tipo2)
    try:
        cursor.execute(sql, values)
        connection.commit()
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=400, detail="El número de Pokédex ya existe")
    finally:
        cursor.close()
        connection.close()
    return pokemon

# Actualizar un Pokémon
#@app.put("/pokemons/{numero_pokedex}", response_model=Pokemon)
#def update_pokemon(numero_pokedex: int, pokemon: Pokemon):
#    connection = get_db_connection()
#    cursor = connection.cursor()
#    sql = "UPDATE pokemon SET imagen=%s, nombre=%s, tipo1=%s, tipo2=%s WHERE numero_pokedex=%s"
#    values = (pokemon.imagen, pokemon.nombre, pokemon.tipo1, pokemon.tipo2, numero_pokedex)
#    cursor.execute(sql, values)
#    connection.commit()
#    cursor.close()
#    connection.close()
#    if cursor.rowcount == 0:
#        raise HTTPException(status_code=404, detail="Pokémon no encontrado")
#    return pokemon

@app.patch("/pokemons/{numero_pokedex}")
def update_pokemon(numero_pokedex: int, pokemon: PokemonUpdate):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Verificar si el Pokémon existe
    cursor.execute("SELECT * FROM pokemon WHERE numero_pokedex = %s", (numero_pokedex,))
    existing_pokemon = cursor.fetchone()
    if not existing_pokemon:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Pokémon no encontrado")

    # Construir la consulta dinámicamente
    update_fields = {key: value for key, value in pokemon.dict().items() if value is not None}
    
    if not update_fields:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="No se han proporcionado campos para actualizar")

    sql = "UPDATE pokemon SET " + ", ".join(f"{key} = %s" for key in update_fields.keys()) + " WHERE numero_pokedex = %s"
    values = list(update_fields.values()) + [numero_pokedex]

    cursor.execute(sql, values)
    connection.commit()
    
    cursor.close()
    connection.close()

    return {"message": "Pokémon actualizado exitosamente", "updated_fields": update_fields}

# Eliminar un Pokémon
@app.delete("/pokemons/{numero_pokedex}")
def delete_pokemon(numero_pokedex: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM pokemon WHERE numero_pokedex = %s", (numero_pokedex,))
    connection.commit()
    cursor.close()
    connection.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Pokémon no encontrado")
    return {"message": "Pokémon eliminado exitosamente"}

