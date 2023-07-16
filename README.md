## Description
This is my first API, built using FastAPI and incorporating data analysis with Pandas, NumPy, and other tools to extract useful information. **This API is only using pokemons of the first generation!!**

## Documentation
The api changes the "pokemon of the day" every 15 minutes.
You can find the complete documentation in detail at `/docs` or `/redoc`.

| Request                   | Type | Description                                              |
|---------------------------|------|----------------------------------------------------------|
| `/`                       | GET  | Returns list of all pokemon                              |
| `/random`                 | GET  | Returns a random pokemon                                 |
| `/pokemon/{id}`           | GET  | Returns the pokemon that matches the pokedex number      |
| `/pokemon/?{parameters}=` | GET  | Returns list of pokemon that matches the parameters      |
| `/answer` {pokedex_number}| POST | Returns if the answer is correct or clues to discover it |


#### Parameters for `/pokemon/`
| Parameters   | Type  | Description                                          |
|--------------|-------|------------------------------------------------------|
|`name`        |`str`  | Returns pokemons that contain the string in the name |
|`type1`       |`str`  | Returns the pokemons that are of the indicated type  |
|`tpye2`       |`str`  | Returns the pokemons that are of the indicated type  |
|`is_legendary`|`int`  | Returns legendary(1) or non-legendary(0) pokemons    |
|`height_m`    |`float`| Returns pokemons that matches the height, in meters  |
|`weight_kg`   |`float`| Returns pokemons that matches the weight, in Kg      |

## Author
**Martín Piampiani**

* [LinkedIn](https://www.linkedin.com/in/martin-piampiani)
* [Portfolio web](https://1pampu.github.io/my-portfolio/)

## See live Example
- [Public API Link](https://my-poke-api.onrender.com/)

## Hiring
If you want to hire me, you can email me at piampianimartin@gmail.com for inquiries.
