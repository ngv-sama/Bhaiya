from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import base64
from PIL import Image
import io
import traceback
import firebase_admin
from firebase_admin import credentials, auth
import os
import uuid
import hashlib
import json
from datetime import datetime
import logging
from dotenv import load_dotenv
from io import BytesIO
import pycurl
from utils import (
    getcategoriesFromImage,
    getCategoriesFromText,
    getCategoriesFromQuery,
    getImage,
)
from similarity import find_top_k_similar
from pymongo import MongoClient

load_dotenv("/Users/rachitdas/Desktop/newBhaiya/Bhaiya/bhAIya-remastered/backend/.env")

mongoDatabase = MongoClient(os.getenv("CONNECTION_STRING"))["bhAIya"]

# DATABASE_NAME="database"
# DATABASE_NAME="database_500"
# DATABASE_NAME="amazon_database"
DATABASE_NAME = "only_clothes"

# IMAGES_DATABASE= "imageDatabase"
# IMAGES_DATABASE= "imageDatabase_500"
# IMAGES_DATABASE = "amazon_images"
IMAGES_DATABASE = "only_clothes_images"


try:
    # database = mongoDatabase["database"].find({}, {"_id": 0})
    # database = mongoDatabase["database_500"].find({}, {"_id": 0})
    database = mongoDatabase[DATABASE_NAME].find({}, {"_id": 0})
    database = list(database)
    print("Data loaded")
except Exception as e:
    print("Error loading main database")
try:
    # imgDatabase = mongoDatabase["imageDatabase"].find({}, {"_id": 0})
    # imgDatabase = mongoDatabase["imageDatabase_500"].find({}, {"_id": 0})
    imgDatabase = mongoDatabase[IMAGES_DATABASE].find({}, {"_id": 0})
    imgDatabase = list(imgDatabase)
    print("Image database loaded")
except Exception as e:
    print("Error loading image database")

# load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

BACKEND_URL = os.getenv("BACKEND_URL_SERVER")
OLLAMA_URL = os.getenv("OLLAMA_URL_SERVER")
json
cred = credentials.Certificate(
    "/Users/rachitdas/Desktop/newBhaiya/Bhaiya/bhAIya-remastered/bhaiya-ee84c-firebase-adminsdk-w4fz2-15489a0102.json"
)
firebase_admin.initialize_app(cred)

# def ollama_request(model, prompt, image=None):
#     url = f"{OLLAMA_URL}/api/generate"
#     data = {
#         "model": model,
#         "prompt": prompt,
#         "stream": False
#     }
#     if image:
#         data["images"] = [image]

#     response = requests.post(url, json=data)
#     if response.status_code == 200:
#         return response.json()["response"]
#     else:
#         raise Exception(f"Ollama request failed: {response.text}")

def ollama_request(model, prompt, image=None):
    url = f"{OLLAMA_URL}/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    if image:
        data["images"] = [image]
    
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, json.dumps(data))
    
    try:
        c.perform()
        status_code = c.getinfo(pycurl.HTTP_CODE)
        if status_code == 200:
            body = buffer.getvalue().decode('utf-8')
            return json.loads(body)["response"]
        else:
            raise Exception(f"Ollama request failed: {buffer.getvalue().decode('utf-8')}")
    finally:
        c.close()


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/verify_token', methods=['POST'])
def verify_token():
    id_token = request.json['idToken']
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token['email']
        session['logged_in'] = True
        session['user_type'] = 'user'
        session['email'] = email
        session['uuid'] = hashlib.sha256(email.encode()).hexdigest()
        session['username'] = email.split('@')[0]
        return jsonify({"success": True}), 200
    except auth.InvalidIdTokenError:
        return jsonify({"error": "Invalid token"}), 400

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    user_type = request.form.get('user_type')
    
    if username and password:  # Add your authentication logic here
        session['logged_in'] = True
        session['user_type'] = user_type
        session['email'] = email
        session['username'] = username
        session['uuid'] = hashlib.sha256(username.encode()).hexdigest()
        logging.info(f"User {username} logged in")
        if user_type == 'user':
            return redirect(url_for('index'))
        else:
            return redirect('http://localhost:8501')
    else:
        return render_template('login.html', error="Invalid credentials")

@app.route('/get_profile', methods=['GET'])
def get_profile():
    if not session.get('logged_in'):
        return jsonify({"error": "Not logged in"}), 401
    
    return jsonify({
        "username": session['username'],
        "email": session['email']
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    return render_template('dash.html')

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    if not session.get('logged_in'):
        return jsonify({"error": "Not logged in"}), 401

    desc = request.form.get('description')
    image = request.files.get('image')

    data = {}
    if desc:
        data['text'] = desc

    print("Sending to FastAPI:", data)

    if image and image.filename:
        try:
            img = Image.open(image)
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            image_data = base64.b64encode(buffered.getvalue()).decode()
            data['img64'] = image_data
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return jsonify({"error": f"Error processing image: {str(e)}"}), 500

    textCategories = None
    imgCategories = None
    text = data.get("text", None)
    img64 = data.get("img64", None)
    if img64:
        if img64[0] == "b":
            img64 = img64[2:-1]
    categories = {}
    print(text)
    if text != None:
        textCategories = getCategoriesFromQuery("llama3.1:8b", text, ollama=True)[
            "categories"
        ][0]
    if img64 != None:
        imgCategories = getcategoriesFromImage(
            "llava-phi3:latest", imagePath=None, imgb64=img64, ollama=True
        )["categories"][0]
    if text != None and img64 != None:
        for key in textCategories.keys():
            categories[key] = list(set(textCategories[key] + imgCategories[key]))
    elif text != None:
        categories = textCategories
    else:
        categories = imgCategories
    print(categories)
    results = find_top_k_similar(categories, database, top_k=5)
    l = []
    for result in results:
        result[1]["image"] = getImage(imgDatabase, result[1]["id"])
        l.append(result[1])
    
    return l

    # try:
    #     response = requests.post(f"{BACKEND_URL}/data", json=data)

    #     if response.ok:
    #         result = response.json()
    #         return jsonify(result)
    #     else:
    #         return jsonify({"error": f"FastAPI error: {response.text}"}), 500
    # except requests.exceptions.RequestException as e:
    #     print(f"Error communicating with FastAPI: {str(e)}")
    #     return jsonify({"error": f"Error communicating with FastAPI: {str(e)}"}), 500
    # except Exception as e:
    #     print(f"Unexpected error: {str(e)}")
    #     print(traceback.format_exc())
    #     return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/item/<string:item_id>')
def item_page(item_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('item.html', item_id=str(item_id))

@app.route('/save_chat_history', methods=['POST'])
def save_chat_history():
    if not session.get('logged_in'):
        return jsonify({"error": "Not logged in"}), 401

    user_uuid = session['uuid']
    data = request.json

    # Create a unique file for each user
    user_file = f'chat_history_{user_uuid}.json'

    user_data = {
        "email": session['email'],
        "last_updated": datetime.now().isoformat(),
        "conversations": data['conversations'],
        "currentConversationId": data['currentConversationId']
    }
    
    with open(user_file, 'w') as f:
        json.dump(user_data, f)
    
    return jsonify({"message": "Chat history saved successfully"}), 200

@app.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    if not session.get('logged_in'):
        return jsonify({"error": "Not logged in"}), 401

    user_uuid = session['uuid']
    user_file = f'chat_history_{user_uuid}.json'

    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            user_history = json.load(f)
        return jsonify(user_history), 200
    else:
        return jsonify({"conversations": {}, "currentConversationId": None}), 200


@app.route('/get_details', methods=['POST'])
def get_details():
    if not session.get('logged_in'):
        return jsonify({"error": "Not logged in"}), 401
    
    product_id = request.json.get('id')
    print("Product ID:", product_id)

    id_data={"id":str(product_id)}
    
    try:
        data=id_data
        # response = requests.post(f"{BACKEND_URL}/getCategories", json=id_data)
        # if response.ok:
        id = data["id"]
        # data=mongoDatabase["database"].find({"id":int(id)},{"_id":0})
        # data=mongoDatabase["database_500"].find({"id":str(id)},{"_id":0})
        try:
            data = mongoDatabase[DATABASE_NAME].find({"id": str(id)}, {"_id": 0})
            imageData = getImage(imgDatabase, str(id))
            data_send = list(data)[0]

        except Exception as e:
            data = mongoDatabase[DATABASE_NAME].find({"id": int(id)}, {"_id": 0})
            imageData = getImage(imgDatabase, int(id))
            data_send = list(data)[0]
        data_send["image"] = imageData
        product_details = data_send
        return jsonify(product_details)
        # else:
        #     return jsonify({"error": f"Backend error: {response.text}"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error communicating with backend: {str(e)}"}), 500

@app.route('/product_chat', methods=['POST'])
def product_chat():
    if not session.get('logged_in'):
        return jsonify({"error": "Not logged in"}), 401

    product_id = request.json.get('id')
    user_message = request.json.get('message')
    product_description = request.json.get('description', '')

    try:
        # Fetch product details from FastAPI backend
        # response = requests.post(f"{BACKEND_URL}/getCategories", json={"id": product_id})
        data = {"id": product_id}
        id = data["id"]
        # data=mongoDatabase["database"].find({"id":int(id)},{"_id":0})
        # data=mongoDatabase["database_500"].find({"id":str(id)},{"_id":0})
        try:
            data = mongoDatabase[DATABASE_NAME].find({"id": str(id)}, {"_id": 0})
            imageData = getImage(imgDatabase, str(id))
            data_send = list(data)[0]

        except Exception as e:
            data = mongoDatabase[DATABASE_NAME].find({"id": int(id)}, {"_id": 0})
            imageData = getImage(imgDatabase, int(id))
            data_send = list(data)[0]
        data_send["image"] = imageData
        # print(data_send)
        product_details=data_send
        del product_details["image"]
        print("These are the product details: ", product_details)
        # Generate a prompt for Llama 3.1
        prompt = f"""
        You are an AI shopping assistant. You have the following product details:
        {product_details}
        Product description: {product_description}
        The customer asks: {user_message}
        Provide a helpful and informative response based on the product details and description.
        """
        # Generate response using Llama 3.1
        response = ollama_request("gemma2:2b", prompt)
        return jsonify({"response": response})

        # if response.ok:
        #     product_details = response.json()
        #     del(product_details['image'])
        #     print("These are the product details: ", product_details)

        #     # Generate a prompt for Llama 3.1
        #     prompt = f"""
        #     You are an AI shopping assistant. You have the following product details:
        #     {product_details}

        #     Product description: {product_description}

        #     The customer asks: {user_message}

        #     Provide a helpful and informative response based on the product details and description.
        #     """

        #     # Generate response using Llama 3.1
        #     response = ollama_request("gemma2:2b", prompt)

        #     return jsonify({"response": response})
        # else:
        #     return jsonify({"error": f"Backend error: {response.text}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error in product chat: {str(e)} this is payload {product_details.keys()}"}), 500

@app.route('/generate_image_description', methods=['POST'])
def generate_image_description():
    if not session.get('logged_in'):
        return jsonify({"error": "Not logged in"}), 401

    product_id = request.json.get('id')

    try:
        # Fetch product details from FastAPI backend
        # response = requests.post(f"{BACKEND_URL}/getCategories", json={"id": product_id})
        # if response.ok:
        data = {"id": product_id}
        id = data["id"]
        # data=mongoDatabase["database"].find({"id":int(id)},{"_id":0})
        # data=mongoDatabase["database_500"].find({"id":str(id)},{"_id":0})
        try:
            data = mongoDatabase[DATABASE_NAME].find({"id": str(id)}, {"_id": 0})
            imageData = getImage(imgDatabase, str(id))
            data_send = list(data)[0]

        except Exception as e:
            data = mongoDatabase[DATABASE_NAME].find({"id": int(id)}, {"_id": 0})
            imageData = getImage(imgDatabase, int(id))
            data_send = list(data)[0]
        data_send["image"] = imageData
        product_details = data_send
        image_data = product_details.get('image')
        if(image_data):
            if(image_data[0]=='b'):
                image_data=image_data[2:-1]

        if not image_data:
            return jsonify({"error": "No image data found"}), 400

        # Generate image description using LLaVA
        prompt = "Describe this product image in detail."
        description = ollama_request("llava", prompt, image=image_data)

        return jsonify({"description": description})
        # else:
        #     return jsonify({"error": f"Backend error: {response.text}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error generating image description: {str(e)}"}), 500


if __name__ == '__main__':
    # app.run(debug=True,port=5002)
    app.run()
