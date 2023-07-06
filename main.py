# Import Libraries
import json
import random
from fastapi import FastAPI

# Import our pokemon database into a list
dbRoute = "DataBase\pokemon-used.json"
with open(dbRoute,'r') as file:
    contentJson = json.load(file)
pokemonList = list(contentJson)

# Create a new instance of the FastAPI application
app = FastAPI()

# Returns all the pokemon list
@app.get("/")
async def pokedex():
    return pokemonList

# Returns pokemon that contains that number in the pokedex
@app.get("/{numPokedex}")
async def searchPokemon(numPokedex: int):
    if(numPokedex > len(pokemonList)): return {"message":"That pokemon doesn't exist in the 1st gen!"}
    return pokemonList[numPokedex - 1]

# Return random pokemon when requested
@app.get("/random")
async def pokeRandom():
    return random.choice(pokemonList)