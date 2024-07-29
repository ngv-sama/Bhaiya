from fastapi import FastAPI
import uvicorn
from utils import getcategoriesFromImage,getCategoriesFromText,getImage
from similarity import find_top_k_similar
import json
import os 
from dotenv import load_dotenv

load_dotenv()

database_path = os.getenv("SAMPLE_DATABASE_NORMAL")
images_path = os.getenv("SAMPLE_DATABASE_IMAGE")

app=FastAPI()
@app.get("/")
async def root():
    return {"message":"App is running"}

@app.post("/data")
async def data(data:dict):
    database=None
    imgDatabase=None
    textCategories=None
    imgCategories=None
    try:
        with open(database_path,"r") as f:
            database=json.load(f)
    except Exception as e:
        print(f"An error occured while reading the database: {e}")
    try:
        with open(images_path,"r") as f:
            imgDatabase=json.load(f)
    except Exception as e:
        print(f"An error occured while reading the image database: {e}")
    text=data.get("text",None)
    img64=data.get("img64",None)
    categories={}
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


if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=5004)
