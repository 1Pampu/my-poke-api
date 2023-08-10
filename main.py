# Import Libraries
import json
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

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
lastPkmon = random.choice(pokemonList)
lastPkmon = lastPkmon["name"]
pkmonday = random.choice(pokemonList)

# Function that changes the pokemon of the day
def changePokemonDay():
    global pkmonday,lastPkmon
    # Update last pokemon
    lastPkmon = pkmonday["name"]
    # Update pokemonday
    pkmonday = random.choice(pokemonList)

# Create the automatization of the change of pokemon
scheduler = BackgroundScheduler(timezone=pytz.utc)
trigger = CronTrigger(minute="0,30")  # Execute when minutes are 0 and 30
scheduler.add_job(changePokemonDay, trigger=trigger)
scheduler.start()

# Returns when it's the next change
@app.get("/time")
async def nextRun():
    next_run = scheduler.get_jobs()[0].next_run_time
    nextChange = next_run.astimezone(pytz.utc).replace(microsecond=0).isoformat() + 'Z'
    return {"nextPokemon": nextChange}

# Returns the last pokemon chosen
@app.get("/lastGuess")
async def lastGuess():
    return {"pokemon":lastPkmon}


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

        if guessPokemon["pokedex_number"] == pkmonday["pokedex_number"]: pdex = True
        elif guessPokemon["pokedex_number"] > pkmonday["pokedex_number"]: pdex = "lower"
        else: pdex = "higher"

        if guessPokemon["type1"].lower() == pkmonday["type1"].lower(): primaryType = True
        else: primaryType = False

        if guessPokemon["type2"].lower() == pkmonday["type2"].lower(): secondaryType = True
        else: secondaryType = False

        if guessPokemon["is_legendary"] == pkmonday["is_legendary"]: legendary = True
        else: legendary = False

        if guessPokemon["height_m"] == pkmonday["height_m"]: height = True
        elif guessPokemon["height_m"] > pkmonday["height_m"]: height = "lower"
        else: height = "higher"

        if guessPokemon["weight_kg"] == pkmonday["weight_kg"]: weight = True
        elif guessPokemon["weight_kg"] > pkmonday["weight_kg"]: weight = "lower"
        else: weight = "higher"

        return {"pokedex_number": pdex,"type1":primaryType,"type2":secondaryType,"is_legendary": legendary,"height_m": height,"weight_kg":weight}

    # If not valid pokemon
    else:
        raise HTTPException(status_code=404,detail="That's not a valid Pokemon!")