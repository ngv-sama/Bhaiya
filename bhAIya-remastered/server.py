from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import base64
from PIL import Image
import io
import traceback
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

BACKEND_URL = os.getenv("BACKEND_URL_SERVER")  # Updated to match your FastAPI port

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user_type = request.form.get('user_type')
    
    # Here you would typically verify the credentials against a database
    # For this example, we'll use a simple check
    if username and password:  # Add your authentication logic here
        session['logged_in'] = True
        session['user_type'] = user_type
        if user_type == 'user':
            return redirect(url_for('index'))
        else:
            return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error="Invalid credentials")

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
    
    print("Form data received:", request.form)
    print("Files received:", request.files)

    desc = request.form.get('description')
    image = request.files.get('image')
    
    data = {}
    if desc:
        data['text'] = desc

    if image and image.filename:  # Check if image is actually uploaded
        try:
            img = Image.open(image)
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            image_data = base64.b64encode(buffered.getvalue()).decode()
            data['img64'] = image_data
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return jsonify({"error": f"Error processing image: {str(e)}"}), 500

    print("Data being sent to FastAPI:", data)

    try:
        print(f"Sending data to FastAPI: {data}")  # Log the data being sent
        response = requests.post(f"{BACKEND_URL}/data", json=data)
        print(f"FastAPI response status: {response.status_code}")  # Log the response status
        
        if response.ok:
            result = response.json()
            return jsonify(result)
        else:
            return jsonify({"error": f"FastAPI error: {response.text}"}), 500
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with FastAPI: {str(e)}")
        return jsonify({"error": f"Error communicating with FastAPI: {str(e)}"}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())  # Print the full traceback
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

if __name__ == '__main__':
    app.run(debug=True)
