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

def getCategoriesFromQuery(modelname, query, ollama=True, session=None, use_pycurl=True):
    prompt = f"""
    [INST]
        Your task is to generate relevant product categories based on the user's search query: "{query}". Generate categories that would be suitable for products matching this query. Provide the output in JSON format, following these guidelines strictly:

        1. Generate categories following these steps:
        - Identify main categories that broadly encompass products related to the search query.
        - Generate subcategories that further specify types of products within the main categories.
        - Include additional details or categories that might be relevant to the search query.

        2. Follow these JSON formatting rules:
        - No additional text should be generated, only the JSON object with the categories.
        - Use double quotes for all string values.
        - No trailing commas after the last item in lists or objects.
        - Do not enclose the response in any type of code block.
        - The categories key should contain a list with one dictionary.
        - 'Main category', 'Sub categories', and 'Additional details' should each be a list containing comma-separated strings.

        3. Consider these points while generating categories:
        - Focus on general product categories rather than specific brands.
        - Include relevant attributes like occasion, season, target demographic, etc., when applicable.
        - Consider various interpretations of the query to provide a comprehensive set of categories.

        The response format should be:
        {{
            "categories": [{{
                "Main category": ["Generated main categories..."],
                "Sub categories": ["Generated sub categories..."],
                "Additional details": ["Generated additional details or categories..."]
            }}]
        }}

        Example 1:
        Query: "Can you please help me with some winter holiday gift suggestions"
        {{
            "categories": [{{
                "Main category": ["Gifts", "Holiday Items"],
                "Sub categories": ["Decorations", "Accessories", "Home Decor"],
                "Additional details": ["Winter", "Festive", "Family", "Traditional", "Modern"]
            }}]
        }}

        - Ensure that the response includes three fields: Main category, Sub categories, and Additional details.
        - Only return these 3 fields in the response. Include all details within these fields only.
        - Do not add any aditional text apart from these fields 
    [/INST]
    """
    res = ""
    if ollama:
        try:
            print("Processing text..")
            data = {
                "model": modelname,
                "prompt": prompt,
                "format": "json",
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
        print(res)
        res = json.loads(res)
    except Exception as e:
        print("Exception occurred while parsing the response: ", e)
        res = None
    return res
    



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



#personalised disocunt function 

def get_max_values(customers):
    max_purchase_value = max(customer['avg_purchase_value'] for customer in customers)
    max_discount_usage = max(customer['discount_usage'] for customer in customers)
    max_purchase_frequency = max(customer['purchase_frequency'] for customer in customers)
    max_purchase_recency = max(customer['purchase_recency'] for customer in customers)
    
    return max_purchase_value, max_discount_usage, max_purchase_frequency, max_purchase_recency

def calculate_score_and_discount(avg_purchase_value, max_purchase_value, discount_usage, max_discount_usage, 
                                  purchase_frequency, max_purchase_frequency, purchase_recency, max_recency, 
                                  product_category=None):
    # Calculate the weighted score based on customer attributes
    score = (0.3 * (avg_purchase_value / max_purchase_value)) + \
            (0.2 * (discount_usage / max_discount_usage)) + \
            (0.3 * (purchase_frequency / max_purchase_frequency)) + \
            (0.2 * (purchase_recency / max_recency))
    
    # Determine discount based on the calculated score
    if score > 0.8:
        discount = 0.20  # 20% discount for high-value customers
    elif score > 0.5:
        discount = 0.10  # 10% discount for moderate-value customers
    else:
        discount = 0.05  # 5% discount for low-value customers
    
    # Additional discount for specific product categories (e.g., electronics)
    if product_category == "electronics":
        discount += 0.05
    
    return score, discount * 100  # Return score and discount percentage
