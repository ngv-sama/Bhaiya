from flask import Flask, render_template, request, jsonify
import requests
import base64
from PIL import Image
import io
import traceback

app = Flask(__name__)

BACKEND_URL = "http://127.0.0.1:8000"  # Updated to match your FastAPI port

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
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
        # print(f"FastAPI response content: {response.text}")  # Log the response content
        
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
    item_details = {
        "id": item_id,
        "price": "N/A",
        "image": "placeholder_image_data"
    }
    return render_template('item.html', item=item_details)

if __name__ == '__main__':
    app.run(debug=True)