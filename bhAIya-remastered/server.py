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

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

BACKEND_URL = os.getenv("BACKEND_URL_SERVER")

cred = credentials.Certificate("bhaiya-ee84c-firebase-adminsdk-w4fz2-15489a0102.json")
firebase_admin.initialize_app(cred)


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
        session['chat_history'] = []
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
        session['chat_history'] = []
        logging.info(f"User {username} logged in")
        logging.info(f"Chat History Initialized  to: {session['chat_history']}")
        if user_type == 'user':
            return redirect(url_for('index'))
        else:
            return redirect(url_for('dashboard'))
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
    if 'chat_history' in session and session['chat_history']:
        save_chat_history()
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

    try:
        response = requests.post(f"{BACKEND_URL}/data", json=data)
        
        if response.ok:
            result = response.json()
            # Save the user's question and the assistant's response
            session['chat_history'].append({
                'user': data,
                'assistant': result
            })
            return jsonify(result)
        else:
            return jsonify({"error": f"FastAPI error: {response.text}"}), 500
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with FastAPI: {str(e)}")
        return jsonify({"error": f"Error communicating with FastAPI: {str(e)}"}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/item/<int:item_id>')
def item_page(item_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    item_details = {
        "id": item_id,
        "price": "N/A",
        "image": "placeholder_image_data"
    }
    return render_template('item.html', item=item_details)

@app.route('/save_chat_history', methods=['GET'])
def save_chat_history():
    if not session.get('logged_in'):
        return jsonify({"error": "Not logged in"}), 401
    
    chat_history = session.get('chat_history', [])
    if not chat_history:
        return jsonify({"message": "No chat history to save"}), 200

    data = {
        "uuid": session['uuid'],
        "email": session['email'],
        "chat_date": datetime.now().isoformat(),
        "chat_history": chat_history
    }

    logging.info("Sending Data to Backend...", flush=True)

    try:
        response = requests.post(f"{BACKEND_URL}/chat_history", json=data)
        if response.ok:
            session['chat_history'] = []  # Clear the chat history after saving
            return jsonify({"message": "Chat history saved successfully"}), 200
        else:
            return jsonify({"error": f"Error saving chat history: {response.text}"}), 500
    except Exception as e:
        print(f"Error saving chat history: {str(e)}")
        return jsonify({"error": f"Error saving chat history: {str(e)}"}), 500

@app.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    if not session.get('logged_in'):
        return jsonify({"error": "Not logged in"}), 401

    try:
        response = requests.get(f"{BACKEND_URL}/chat_history/{session['uuid']}")
        if response.ok:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": f"Error fetching chat history: {response.text}"}), 500
    except Exception as e:
        print(f"Error fetching chat history: {str(e)}")
        return jsonify({"error": f"Error fetching chat history: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)