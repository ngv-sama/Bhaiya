import os
import requests
from langchain_community.llms import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
import json
from base64 import b64encode
import sys
from dotenv import load_dotenv

load_dotenv()

BASEURL=os.getenv("BASEURL")
# BASEURL = 'http://localhost:11434'
HUGGINGFACETOKEN = os.getenv("HUGGINGFACETOKEN")

def encodedimage(imgPath):
    try:
        with open(imgPath,"rb") as imgFile:
            return b64encode(imgFile.read())
    except Exception as e:
        print(f"An error occured while encoding the image: {e}")
        return None

def getImage(imgDatabase,id):
    for item in imgDatabase:
        if(item["id"]==id):
            return item["image"]
    return ""

def getCategoriesFromText(modelname,description,ollama=True):
    prompt = f"""
            [INST]
                Your primary task is to assign categories to the product description {description}. The product description may or may not make sense gramatically your job is to extract the categories keeping these points in mind. Give the output in JSON format. Follow these JSON structure guidelines strictly and provide the response in JSON only, without any explanatory text.

                1.Follows these steps to extract categories:
                - Extract the main categories pertaining to the product description. The main categories should be extracted based on the context of the product description.
                - Extract the subcategories pertaining to the product description. The subcategories should be extracted based on the context of the product description.
                - Extract any more additional details or categories if you find them.

                2. Ensure you follow these **JSON formatting rules**:
                -Use double quotes for all string values.
                -No trailing commas after the last item in lists or objects.
                -Remove the introductory text and final note from JSON.
                -Do not enclose the response in any type of code block.

                The response format should be:
                {{
                    "categories": [{{
                        "Main category": ["Extracted main categories...."],
                        "Sub categories": ["Extracted sub categories...."],
                        "Additional details": ["Extracted additional details or categories...."]
                    }}]
                }}
            [/INST]
            """
    res = ""
    if(ollama):
        try:
            print("Processing text..")
            with requests.post(f"{BASEURL}/api/generate",json={"model":modelname,"prompt":prompt},stream=True) as response:
                print(response)
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if not chunk.get("done"):
                            response_piece = chunk.get("response", "")
                            res+=response_piece
                        else:
                            break
        except Exception as e:
            print(f"An error occured with ollama using text: {e}")
    else:
        try:
            print("Processing text...")
            modelIns = HuggingFaceEndpoint(
                repo_id="mistralai/Mistral-7B-Instruct-v0.3",
                huggingfacehub_api_token="token_here",
            )
            res=modelIns.invoke(prompt)
            print(res)
        except Exception as e:
            print(f"Error when API is used: {e}")
            pass
    try:
        res = json.loads(res)
    except Exception as e:
        print("Exception occured while parsing the response: ",e)
        res=None
    return res

def getcategoriesFromImage(modelname,imagePath,imgb64=None,ollama=True):
    prompt = f"""
            [INST]
                Your primary task is to extract categories from the product's image. Your job is to extract the categories keeping these points in mind. Give the output in JSON format.Follow these JSON structure guidelines strictly and provide the response in JSON only, without any explanatory text.

                1.Follows these steps to extract categories:
                - Extract the main categories pertaining to the product image. The main categories should be extracted based on the context of the product image.
                - Extract the subcategories pertaining to the product image. The subcategories should be extracted based on the context of the product image.
                - Extract any more additional details or categories if you find them.

                2. Ensure you follow these **JSON formatting rules**:
                - Use double quotes for all string values.
                - No trailing commas after the last item in lists or objects.
                -Remove the introductory text and final note from JSON.
                -Do not enclose the response in any type of code block.
                -The categories key should contain a list that has one dictionary

                The response format should be:
                {{
                    "categories": [{{
                        "Main category": ["Extracted main categories...."],
                        "Sub categories": ["Extracted sub categories...."],
                        "Additional details": ["Extracted additional details or categories...."]
                    }}]
                }}
            [/INST]
            """
    res=""
    if(ollama):
        try:
            if(imgb64==None):
                print(f"Processing image {imagePath} ...")
                imageb64 = encodedimage(imagePath)
            else:
                imageb64=imgb64
            with requests.post(f"{BASEURL}/api/generate",json={"model":modelname,"prompt":prompt,"images":[imageb64]},stream=True) as response:
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if not chunk.get("done"):
                            response_piece = chunk.get("response", "")
                            res+=response_piece
                        else:
                            break
                print("response received from ollama")
        except Exception as e:
            print(f"An error occured with ollama using image: {e}")
    else:
        pass
    try:
        res = json.loads(res[8:-4].strip())
    except Exception as e:
        print("Exception occured while parsing the response: ",e)
        res=""
        with requests.post(
            f"{BASEURL}/api/generate",
            json={"model": modelname, "prompt": "Describe the image in a few words", "images": [imageb64]},
            stream=True,
        ) as response:
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if not chunk.get("done"):
                        response_piece = chunk.get("response", "")
                        res += response_piece
                    else:
                        break
        res=getCategoriesFromText("mistral",res,ollama=True)
    return res

# print(
#     getCategoriesFromText(
#         "mistral",
#         "Men Apparel Topwear Shirts Navy Blue Fll 2011 Casual Turtle Check Men Navy Blue Shirt",
#         ollama=False,
#     )
# )

# print(getcategoriesFromImage("llava", "/Users/rachitdas/Desktop/data/images/14147.jpg"))
