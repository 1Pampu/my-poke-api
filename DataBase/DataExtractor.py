# Import Libraries
import pandas as pd
import numpy as np
import os
from PIL import Image
import base64

# Import the original dataset, extracted from  https://www.kaggle.com/datasets/rounakbanik/pokemon
dataFrameRoute = "DataBase/pokemon.csv"
OriginalDataFrame = pd.read_csv(dataFrameRoute)

# Create new dataFrame with relevant data for the app
newDataFrame = OriginalDataFrame[["pokedex_number","name","type1","type2","is_legendary","generation","height_m","weight_kg"]]

# Keep only the 1st gen pokemon
toKeep = np.where(newDataFrame["generation"] == 1)
newDataFrame = newDataFrame.iloc[toKeep]

# Remove extra columns
newDataFrame = newDataFrame.drop("generation", axis=1)

# Fix pokemon names, no special characters \ . '
newDataFrame["name"] = newDataFrame["name"].replace("Nidoran\u2640","Nidoran-f")
newDataFrame["name"] = newDataFrame["name"].replace("Nidoran\u2642","Nidoran-m")
newDataFrame["name"] = newDataFrame["name"].replace("Mr. Mime","Mr-Mime")
newDataFrame["name"] = newDataFrame["name"].replace("Farfetch'd","Farfetchd")

#Add image column, images extracted from https://www.kaggle.com/datasets/vishalsubbiah/pokemon-images-and-types
imageFolderRoute = "DataBase/images"
imageNames = os.listdir(imageFolderRoute)
newDataFrame["image"] = ""
for index, row in newDataFrame.iterrows():
    pokemonName = row["name"]
    imageName = pokemonName.lower() + ".png"
    if imageName in imageNames:
        imageRoute = os.path.join(imageFolderRoute,imageName)
        # Enconde to Base64
        with open(imageRoute, "rb") as imageFile:
            imageContent = imageFile.read()
            imageBase64 = base64.b64encode(imageContent).decode('utf-8')
        newDataFrame.at[index,"image"] = imageBase64
    else:
        print("Not found!")
        print(pokemonName)

# Put special characters again
newDataFrame["name"] = newDataFrame["name"].replace("Nidoran-f","Nidoran\u2640")
newDataFrame["name"] = newDataFrame["name"].replace("Nidoran-m","Nidoran\u2642")
newDataFrame["name"] = newDataFrame["name"].replace("Mr-Mime","Mr. Mime")
newDataFrame["name"] = newDataFrame["name"].replace("Farfetchd","Farfetch'd")

# Change nulls to ""
newDataFrame["type2"].fillna('',inplace=True)

# Finally export data to Json file
newFileRoute = "DataBase/pokemon-used.json"
newDataFrame.to_json(newFileRoute, orient='records')
