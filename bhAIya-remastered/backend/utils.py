import os
import pycurl
import requests
from io import BytesIO
from langchain_community.llms import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
import json
from base64 import b64encode
import sys
from dotenv import load_dotenv

load_dotenv()

BASEURL = os.getenv("BASEURL")
HUGGINGFACETOKEN = os.getenv("HUGGINGFACETOKEN")

def encodedimage(imgPath):
    try:
        with open(imgPath, "rb") as imgFile:
            return b64encode(imgFile.read()).decode("utf-8")
    except Exception as e:
        print(f"An error occurred while encoding the image: {e}")
        return None

def getImage(imgDatabase, id):
    for item in imgDatabase:
        if item["id"] == id:
            return item["image"]
    return ""

import json

def accumulate_response(response):
    res = ""
    
    # Check if response is a string
    if isinstance(response, str):
        lines = response.split('\n')
    else:
        # Assume it's an iterable (like requests.Response)
        lines = response.iter_lines()

    for line in lines:
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        
        if line.strip():
            try:
                chunk = json.loads(line)
                if not chunk.get("done"):
                    response_piece = chunk.get("response", "")
                    res += response_piece
                    # print(response_piece, end='', flush=True)
                else:
                    break
            except json.JSONDecodeError:
                # If it's not valid JSON, just add the line to the result
                res += line + '\n'
                print(line, end='', flush=True)

    return res


def perform_curl_request(url, data, stream=False):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, json.dumps(data))
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    
    accumulated = []

    def write_callback(data):
        decoded_data = data.decode('utf-8')
        buffer.write(data)
        if stream:
            try:
                json_data = json.loads(decoded_data)
                if not json_data.get("done"):
                    response_piece = json_data.get("response", "")
                    # print(response_piece, end='', flush=True)
                    accumulated.append(response_piece)
            except json.JSONDecodeError:
                # Handle incomplete JSON data
                accumulated.append(decoded_data)

    c.setopt(c.WRITEFUNCTION, write_callback)

    try:
        c.perform()
    finally:
        c.close()

    if stream:
        return ''.join(accumulated)
    else:
        return accumulate_response(buffer.getvalue().decode('utf-8'))

def perform_request(url, data, stream=False, use_pycurl=True, session=None):
    if use_pycurl:
        return perform_curl_request(url, data, stream)
    else:
        request_func = session.post if session else requests.post
        response=request_func(url, json=data, stream=stream)
        return accumulate_response(response)

def getCategoriesFromText(modelname, description, ollama=True, session=None, use_pycurl=True):
    prompt = f"""
    [INST]
        Your primary task is to assign categories to the product description {description}. The product description may or may not make sense grammatically your job is to extract the categories keeping these points in mind. Give the output in JSON format. Follow these JSON structure guidelines strictly and provide the response in JSON only, without any explanatory text.

        1.Follows these steps to extract categories:
        - Extract the main categories pertaining to the product description. The main categories should be extracted based on the context of the product description.
        - Extract the subcategories pertaining to the product description. The subcategories should be extracted based on the context of the product description.
        - Extract any more additional details or categories if you find them.
        

        2. Ensure you follow these **JSON formatting rules**:
        - Use double quotes for all string values.
        - No trailing commas after the last item in lists or objects.
        - Remove the introductory text and final note from JSON.
        - Do not enclose the response in any type of code block.
        - The categories key should contain a list that has one dictionary
        - 'Main category', 'Sub categories' and 'Additional details' should be a single list containing all the additional details as comma-separated strings.
        - Ensure that you follow the provided response format.

        3. Ensure you follow these instructions while extracting categories:
        - Do not make assumptions about the brand of the product. 
        - If a brand is mentioned, make sure to include it within the additional details.
        - Use words that can be used to describe the product in a general sense, such as color, pattern, shape, etc.
        - If there is anything in particular about the product that stands out, make sure to include it in the additional details.

        The response format should be:
        {{
            "categories": [{{
                "Main category": ["Extracted main categories...."],
                "Sub categories": ["Extracted sub categories...."],
                "Additional details": ["Extracted additional details or categories...."]
            }}]
        }}

        Here is an examples of how the output should be formatted, use this to only understand the output format and nothing else:
        Example 1:
        {{
            
            "categories": [{{
                "Main category": ["Men's Apparel", "Tops", "T-shirts"],
                "Sub categories": ["Summer Wear", "Casual"],
                "Additional details": ["Puma", "Sports", "Black"]
            }}]

        }}

        Example 2:
        {{
            
            "categories": [{{
                "Main category": ["Men's Apparel", "Sports Wear"],
                "Sub categories": ["Bottomwear", "Track Pants"],
                "Additional details": ["Black", "Fall 2011.0", "Casual", "Manchester United", "Solid"]
            }}]

        }}

    [/INST]
    """
    res = ""
    if ollama:
        try:
            print("Processing text..")
            data = {
                "model": modelname,
                "prompt": prompt,
                "options": {
                    "temperature": 0.2
                },
            }
            res = perform_request(f"{BASEURL}/api/generate", data, stream=False, use_pycurl=use_pycurl, session=session)
        except Exception as e:
            print(f"An error occurred with ollama using text: {e}")
    else:
        try:
            print("Processing text...")
            modelIns = HuggingFaceEndpoint(
                repo_id="mistralai/Mistral-7B-Instruct-v0.3",
                huggingfacehub_api_token="token_here",
            )
            res = modelIns.invoke(prompt)
        except Exception as e:
            print(f"Error when API is used: {e}")
            pass
    try:
        res = json.loads(res)
    except Exception as e:
        print("Exception occurred while parsing the response: ", e)
        res = None
    return res

def getcategoriesFromImage(modelname, imagePath, imgb64=None, ollama=True, session=None, use_pycurl=True):
    prompt = f"""
    <|system|>
        Your primary task is to extract categories from the product's image. Your job is to extract the categories keeping these points in mind. Give the output in JSON format.Follow these JSON structure guidelines strictly and provide the response in JSON only, without any explanatory text.

        1.Follows these steps to extract categories:
        - Extract the main categories pertaining to the product image. The main categories should be extracted based on the context of the product image.
        - Extract the subcategories pertaining to the product image. The subcategories should be extracted based on the context of the product image.
        - Extract any more additional details or categories if you find them.

        2. Ensure you follow these **JSON formatting rules**:
        - Use double quotes for all string values.
        - No trailing commas after the last item in lists or objects.
        - Remove the introductory text and final note from JSON.
        - Do not enclose the response in any type of code block.
        - The categories key should contain a list that has one dictionary
        - 'Main category', 'Sub categories' and 'Additional details' should be a single list containing all the additional details as comma-separated strings.

        3. Ensure you follow these instructions while extracting categories:
        - Do not make assumptions about the brand of the product.
        - Use words that can be used to describe the product in a general sense, such as color, pattern, shape, etc.
        - If there is anything in particular about the product that stands out, make sure to include it in the additional details. Keep the description short and simple, like a category and not a description.
        
    

        The response format should be:
        {{
            "categories": [{{
                "Main category": ["Extracted main categories...."],
                "Sub categories": ["Extracted sub categories...."],
                "Additional details": ["Extracted additional details or categories...."]
            }}]
        }}

        - Ensure that there are 3 fields in the response: Main category, Sub categories, and Additional details.
        - There should be no other fields in the response. All details must be included in these 3 fields only.
        - Ensure that all 3 fields are a single list containing all the details as comma-separated strings.
    <|end|>
    """
    res = ""
    if ollama:
        try:
            if imgb64 is None:
                print(f"Processing image {imagePath} ...")
                imageb64 = encodedimage(imagePath)
            else:
                imageb64 = imgb64
            
            data = {
                "model": modelname,
                "prompt": prompt,
                "images": [imageb64],
                "options": {"temperature": 0.2},
            }
            res = perform_request(f"{BASEURL}/api/generate", data, stream=False, use_pycurl=use_pycurl, session=session)
            print("response received from ollama")
        except Exception as e:
            print(f"An error occurred with ollama using image: {e}")
    else:
        pass
    try:
        res = json.loads(res)
        res = json.loads(res)
    except Exception as e:
        print("Exception occurred while parsing the response: ", e)
        res = ""
        data = {"model": modelname, "prompt": "Describe the image in a few words", "images": [imageb64]}
        res = perform_request(f"{BASEURL}/api/generate", data, stream=True, use_pycurl=use_pycurl, session=session)
        res = getCategoriesFromText("mistral", res, ollama=True, session=session, use_pycurl=use_pycurl)
    return res