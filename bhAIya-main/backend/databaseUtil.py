import os
import sys

import pandas as pd
from utils import getcategoriesFromImage,getCategoriesFromText,encodedimage
import json

class TextDatabaseCreator:
    def __init__(self, data, idColumn, columnsToAccept,priceColumn):
        self.data = data
        self.columnsToAccept = columnsToAccept
        self.idColumn = idColumn
        self.priceColumn=priceColumn

    def create_database(self):
        dataWithNeededColumns = self.data[self.columnsToAccept]
        results={}
        for index, row in dataWithNeededColumns.iterrows():
            id = row[self.idColumn]
            description = ""
            for column in self.columnsToAccept:
                description += str(row[column]) + " "
            res1 = getCategoriesFromText("mistral", description, ollama=True)
            if(res1==None):
                continue
            results[id]=res1["categories"]
            results[id][0]["price"]=row[self.priceColumn]
        return results


class ImageDatabaseCreator:
    def __init__(self, imgfoldername):
        self.imgfolderpath = imgfoldername

    def create_database(self):
        BASE_PATH=f"{os.getcwd()}/{self.imgfolderpath}"
        results={}
        print("Creating Image Database...")
        for filename in os.listdir(BASE_PATH):
            results[int(filename[:filename.index(".")])]=getcategoriesFromImage("llava",f"{BASE_PATH}/{filename}",ollama=True)["categories"]
            results[int(filename[: filename.index(".")])][0]["image"] = encodedimage(
                f"{BASE_PATH}/{filename}"
            )
        return results


class DatabaseCreator:
    def __init__(self, data, idColumn, columnsToAccept, priceColumn,imgfoldername):
        self.data = data
        self.columnsToAccept = columnsToAccept
        self.idColumn = idColumn
        self.imgfoldername = imgfoldername
        self.priceColumn=priceColumn
        self.finalResults={}

    def create_database(self):
        finalResults=[]
        imageResults=[]
        tdc=TextDatabaseCreator(self.data,self.idColumn,self.columnsToAccept,self.priceColumn)
        idc=ImageDatabaseCreator(self.imgfoldername)
        textResult=tdc.create_database()
        imageResult=idc.create_database()
        for key in textResult.keys():
            inter = {}
            inter1={}
            for k in ["Main category", "Sub categories", "Additional details"]:
                try:
                    inter[k] = list(
                        set(
                            textResult.get(key, [{k: []}])[0].get(k, [])
                            + imageResult.get(key, [{k: []}])[0].get(k, [])
                        )
                    )
                except Exception as e:
                    print(textResult)
                    print(imageResult)
                    continue
            inter["id"]=key
            inter["price"]=textResult[key][0]["price"]
            try:
                inter1["image"]=str(imageResult[key][0]["image"])
                inter1["id"]=key
            except Exception as e:
                print("Image not found")
                inter1["image"]=""
                inter1["id"]=key
            finalResults.append(inter)
            imageResults.append(inter1)
        self.finalResults=finalResults
        self.imageResults=imageResults
        return finalResults

    def createJSONDatabase(self):
        with open(f"{os.getcwd()}/database.json", "w") as outfile:
            json.dump(self.finalResults, outfile)
        with open(f"{os.getcwd()}/imageDatabase.json", "w") as outfile:
            json.dump(self.imageResults, outfile)


if __name__=="__main__":
    DATASET_PATH = f"{os.getcwd()}/database.csv"
    columnsToAccept = [
        "id",
        "gender",
        "masterCategory",
        "subCategory",
        "articleType",
        "baseColour",
        "season",
        "year",
        "usage",
        "productDisplayName",
        "price"
    ]
    idColumn = "id"
    priceColumn="price"
    data = pd.read_csv(DATASET_PATH, on_bad_lines="skip")

    # tdc = TextDatabaseCreator(data, idColumn, columnsToAccept,priceColumn)
    # res = tdc.create_database()
    # print(res)

    # idc=ImageDatabaseCreator("images")
    # print(idc.create_database())

    dc = DatabaseCreator(data, idColumn, columnsToAccept, priceColumn,"ImagesBackend")
    dc.create_database()
    dc.createJSONDatabase()
