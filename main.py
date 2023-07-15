# Import Libraries
import json
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import asyncio

# Create a new instance of the FastAPI application
app = FastAPI()

# Allow all origins to use the API
origins= ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import our pokemon database into a list
dbRoute = "DataBase/pokemon-used.json"
#dbRoute = "/opt/render/project/src/DataBase/pokemon-used.json"      # Change the path of where you contain the file
with open(dbRoute,'r') as file:
    contentJson = json.load(file)
pokemonList = list(contentJson)

# Create a pokemon class
class Pokemon(BaseModel):
    name: str

# Variable that contains the pokemon of the "day"
pkmonday = None

# Function that changes the pokemon of the day every X time
async def periodicChange():
    global pkmonDay   # Specify that we are reffering to the global variable
    while True:
        pkmonDay = random.choice(pokemonList)
        await asyncio.sleep(900)   # 900 = 15min

# Start async function at startup
@app.on_event("startup")
async def startTasks():
    asyncio.create_task(periodicChange())

# Returns all the pokemon list
@app.get("/")
async def pokedex():
    return pokemonList

# Returns pokemon that contains that number in the pokedex
@app.get("/pokemon/{numPokedex}")
async def searchByIndexPokemon(numPokedex: int):
    if(numPokedex > len(pokemonList)): raise HTTPException(status_code=404, detail="That pokemon doesn't exist in the 1st gen!")
    return pokemonList[numPokedex - 1]

# Returns list of pokemon that fit the specs
@app.get("/pokemon/")
async def searchByOthers(name: str = None, type1: str = None, type2: str = None, is_legendary: int = None, height_m: float = None, weight_kg: float = None):
    pokemonToReturn = []
    for pokemon in pokemonList:
        qualify = []
        if name != None and name != "": qualify.append(name.lower() in pokemon["name"].lower())
        if (type1 != None and type1 != "") and (type2 != None and type2 != ""):
            qualify.append(type1.lower() == pokemon["type1"] or type1.lower() == pokemon["type2"])
            qualify.append(type2.lower() == pokemon["type1"] or type2.lower() == pokemon["type2"])
        elif type1 != None and type1 != "": qualify.append(type1.lower() == pokemon["type1"] or type1.lower() == pokemon["type2"])
        elif type2 != None and type2 != "": qualify.append(type2.lower() == pokemon["type1"] or type2.lower() == pokemon["type2"])
        if is_legendary != None: qualify.append(is_legendary == pokemon["is_legendary"])
        if height_m != None: qualify.append(height_m == pokemon["height_m"])
        if weight_kg != None: qualify.append(weight_kg == pokemon["weight_kg"])
        if not qualify: qualify.append(False)
        if all(qualify): pokemonToReturn.append(pokemon)
    if not pokemonToReturn:
        raise HTTPException(status_code=404,detail="No pokemon qualifies with those specifications")
    return pokemonToReturn

# Return random pokemon when requested
@app.get("/random/")
async def pokeRandom():
    return random.choice(pokemonList)

# Validate the recived pokemon
@app.post("/answer")
async def validateAnswer(guess: Pokemon):
    if guess.name.lower() == pkmonDay["name"].lower():
        return {"message": "correct answer!"}
    elif any(pokemon["name"].lower() == guess.name.lower() for pokemon in pokemonList):
        return {"message": "incorrect answer"}
    else:
        return {"message": "That pokemon doesn't exist"}