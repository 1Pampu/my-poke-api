# Import Libraries
import pandas as pd
import numpy as np

# Import the original dataset, extracted from  https://www.kaggle.com/datasets/rounakbanik/pokemon
dataFrameRoute = "DataBase/pokemon.csv"
OriginalDataFrame = pd.read_csv(dataFrameRoute)

# Create new dataFrame with relevant data for the app
newDataFrame = OriginalDataFrame[["pokedex_number","name","type1","type2","is_legendary","generation"]]

# Keep only the 1st gen pokemon
toKeep = np.where(newDataFrame["generation"] == 1)
newDataFrame = newDataFrame.iloc[toKeep]

# Remove extra columns
newDataFrame = newDataFrame.drop("generation", axis=1)

# Finally export data to Json file
newFileRoute = "DataBase/pokemon-used.json"
newDataFrame.to_json(newFileRoute, orient='records')