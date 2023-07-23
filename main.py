# Import Libraries
import json
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import asyncio
from datetime import datetime, timedelta,timezone

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

# Variable that contains the pokemon of the "day" and the time to the next change
pkmonday = None
nextChange = None

# Function that changes the pokemon of the day every X time
async def periodicChange():
    global pkmonDay,nextChange   # Specify that we are reffering to the global variable
    while True:
        pkmonDay = random.choice(pokemonList)
        nextChange = datetime.now() + timedelta(minutes=15)
        await asyncio.sleep(900)   # 900 = 15min

# Start async function at startup
@app.on_event("startup")
async def startTasks():
    asyncio.create_task(periodicChange())

# Function to get the time for the next Pokémon change
@app.get("/time")
async def timeToNextPokemon():
    next_change_utc = nextChange.astimezone(timezone.utc).replace(microsecond=0).isoformat() + "Z"
    return {"nextPokemon": next_change_utc}

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

# Create the element that the answer will recieve
class PokedxNumber(BaseModel):
    pokedex_number: int

# Validate the recived pokemon
@app.post("/answer")
async def validateAnswer(guessNumber: PokedxNumber):
    # Response of the server, if all true, the answer is right
    if any(pokemon["pokedex_number"] == guessNumber.pokedex_number for pokemon in pokemonList):
        # Get the pokemon dictionary
        guessPokemon = None
        for pokemon in pokemonList:
            if pokemon["pokedex_number"] == guessNumber.pokedex_number:
                guessPokemon = pokemon
                break

        if guessPokemon["pokedex_number"] == pkmonDay["pokedex_number"]: pdex = True
        elif guessPokemon["pokedex_number"] > pkmonDay["pokedex_number"]: pdex = "lower"
        else: pdex = "higher"

        if guessPokemon["type1"].lower() == pkmonDay["type1"].lower(): primaryType = True
        else: primaryType = False

        if guessPokemon["type2"].lower() == pkmonDay["type2"].lower(): secondaryType = True
        else: secondaryType = False

        if guessPokemon["is_legendary"] == pkmonDay["is_legendary"]: legendary = True
        else: legendary = False

        if guessPokemon["height_m"] == pkmonDay["height_m"]: height = True
        elif guessPokemon["height_m"] > pkmonDay["height_m"]: height = "lower"
        else: height = "higher"

        if guessPokemon["weight_kg"] == pkmonDay["weight_kg"]: weight = True
        elif guessPokemon["weight_kg"] > pkmonDay["weight_kg"]: weight = "lower"
        else: weight = "higher"

        return {"pokedex_number": pdex,"type1":primaryType,"type2":secondaryType,"is_legendary": legendary,"height_m": height,"weight_kg":weight}

    # If not valid pokemon
    else:
        raise HTTPException(status_code=404,detail="That's not a valid Pokemon!")