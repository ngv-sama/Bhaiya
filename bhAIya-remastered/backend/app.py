from fastapi import FastAPI
import uvicorn
from utils import getcategoriesFromImage,getCategoriesFromText,getImage
from similarity import find_top_k_similar
import json
import os 
from dotenv import load_dotenv
from pymongo import MongoClient
import sys

load_dotenv()

database_path = os.getenv("SAMPLE_DATABASE_NORMAL")
images_path = os.getenv("SAMPLE_DATABASE_IMAGE")

mongoDatabase=MongoClient(os.getenv("CONNECTION_STRING"))["bhAIya"]

try:
    database = mongoDatabase["database"].find({}, {"_id": 0})
    database=list(database)
    print("Data loaded")
except Exception as e:
    print("Error loading main database")
try:
    imgDatabase = mongoDatabase["imageDatabase"].find({}, {"_id": 0})
    imgDatabase=list(imgDatabase)
    print("Image database loaded")
except Exception as e:
    print("Erorr loading image database")

app=FastAPI()
@app.get("/")
async def root():
    return {"message":"App is running"}

@app.post("/data")
async def data(data:dict):
    # database=None
    # imgDatabase=None
    textCategories=None
    imgCategories=None
    # try:
    #     with open(database_path,"r") as f:
    #         database=json.load(f)
    # except Exception as e:
    #     print(f"An error occured while reading the database: {e}")
    # try:
    #     with open(images_path,"r") as f:
    #         imgDatabase=json.load(f)
    # except Exception as e:
    #     print(f"An error occured while reading the image database: {e}")
    text=data.get("text",None)
    img64=data.get("img64",None)
    categories={}
    print(text)
    if(text!=None):
        textCategories=getCategoriesFromText("mistral",text,ollama=True)["categories"][0]
    if(img64!=None):
        imgCategories=getcategoriesFromImage("llava",imagePath=None,imgb64=img64,ollama=True)["categories"][0]
    if(text!=None and img64!=None):
        for key in textCategories.keys():
            categories[key]=list(set(textCategories[key]+imgCategories[key]))
    elif(text!=None):
        categories=textCategories
    else:
        categories=imgCategories
    print(categories)
    results=find_top_k_similar(categories,database,top_k=5)
    l=[]
    for result in results:
        result[1]["image"] = getImage(
            imgDatabase,result[1]["id"]
        )
        l.append(result[1])
    return l

@app.post("/addOne")
async def addOne(data:dict):
    """
      Payload
      {"data":{
                  "id":0,
                  "price":123,
                  "Main category":[],
                  "Sub categories":[],
                  "Additional details":[]
              },
              "imgData":{
                    "id":0,
                    "image":"b'/9j/4AAQSk'"
                }
      }
    """
    if(data.get("data",None)):
        print("inserting into main database")
        try:
            x=mongoDatabase["database"].insert_one(data["data"])
            print(x)
        except Exception as e:
            print(e)
            print("Error inserting into main database")

    if(data.get("imgData",None)):
        print("inserting into image database")
        try:
            x=mongoDatabase["imageDatabase"].insert_one(data["imgData"])
            print(x)
        except Exception as e:
            print("Error inserting into image database")


@app.post("/removeOne")
async def removeOne(id:int):
    '''
    Payload : 0(any integer, id to be removed)
    '''
    print("deleting from database")
    try:
        x = mongoDatabase["database"].delete_one({"id": id})
        print(x)
    except Exception as e:
        print("Error deleting from main database")

    try:
        x=mongoDatabase["imageDatabase"].delete_one({"id":id})
        print(x)
    except Exception as e:
        print("Error deleting image database")

@app.post("/addMany")
async def addMany(data:dict):
    """
        payload
        {
            "data":[{
                "id":0,
                "price":123,
                "Main category":[],
                "Sub categories":[],
                "Additional details":[]
            },{
                "id":0,
                "price":123,
                "Main category":[],
                "Sub categories":[],
                "Additional details":[]
            }],
            "imgData":[{
                "id":0,
                "image":"b'/9j/4AAQSk'"

            },{
                "id":0,
                "image":"b'/9j/4AAQSk'"

            }]
        }
    """
    if(data.get("data",None)):
        print("inserting many into database")
        try:
            x = mongoDatabase["database"].insert_many(data.get("data"))
            print(x)
        except Exception as e:
            print("Error inserting many into main database")

    if(data.get("imgData",None)):
        try:
            x = mongoDatabase["imageDatabase"].insert_many(data.get("imgData"))
            print(x)
        except Exception as e:
            print("Error inserting many into image database")


if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=5004)
