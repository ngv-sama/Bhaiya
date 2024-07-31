import streamlit as st
import pymongo
from pymongo import MongoClient
import base64
from PIL import Image
from io import BytesIO
import requests
import pandas as pd

from streamlit_navigation_bar import st_navbar

page = st_navbar(["Home" ,"Add","Remove" ,"Products" ,"Sales","Customer details ","Support"])

st.logo("C:/Users/Administrator 1/Desktop/baby.jpg")

##08082A; 
##extra colour replacement

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background-color: #000018;  /* Black background */
        color: #fff;  /* White text */
    }

    [data-testid="stForm"] {
        background-color: #fff;  /* White form background */
        color: #000;  /* Black form text */
    }

    label, span,h1,h3{
        color: #fff;  /* White text for headings, paragraphs, labels, spans, and list items */
    }
    </style>
    """,
    unsafe_allow_html=True
)
if page =="Home":
    st.title('bhAIya')
    st.title('Seller Dashboard')

# MongoDB connection
client = MongoClient('localhost', 27017)
db = client['bhAIya']
collection_a = db['database']
collection_i = db['imageDatabase']



# Function to encode image to Base64
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# Function to decode Base64 to image
def decode_image(encoded_image):
    image_bytes = base64.b64decode(encoded_image)
    return Image.open(BytesIO(image_bytes))

# Streamlit app code
#action = st.selectbox('Choose Action', ['Add Item', 'Delete Item', 'Upload Image',])


base_url = "http://127.0.0.1:5004"


import requests
if page =="Add":
    st.title('bhAIya - Add products')
        
    actions = ['Select an action', 'Add Item','Upload Image']

    # Use the selectbox with a default placeholder option
    action = st.selectbox('Choose Action', actions)
    # Add Item Form
    if action == 'Add Item':
        with st.form(key='add_item_form'):
            new_id = st.text_input('ID')
            new_masterCategory = st.text_input('Master Category')
            new_sub_categories = st.text_input('Product Display Name')
            new_additional_details = st.text_input('Additional Details')
            new_price = st.text_input('Price')
            submit_button = st.form_submit_button(label='Submit')

            if submit_button:
                new_item = {
                    'Main category': new_masterCategory.split(','),
                    'Sub categories': new_sub_categories.split(','),
                    'Additional details': new_additional_details.split(','),
                    'id': int(new_id),
                    'price': float(new_price),
                }
                response = requests.post(base_url+"/addOne", json={"data": new_item})
                if response.status_code == 200:
                    st.success('Item added successfully!')
                else:
                    st.error('Failed to add item.')

    # Delete Item Form
    

    # Upload Image Form
    elif action == 'Upload Image':
        with st.form(key='upload_image_form'):
            image_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
            image_id = st.text_input('Image ID')
            submit_button = st.form_submit_button(label='Upload')

            if submit_button and image_file:
                image = Image.open(image_file)
                encoded_image = encode_image(image)
                image_item = {
                    
                    'image': "b'"+ encoded_image,
                    'id': int(image_id),
                }
                response = requests.post(base_url+"/addOne", json={"imgData": image_item})
                if response.status_code == 200:
                    st.success('Image uploaded successfully!')
                else:
                    st.error('Failed to upload image.')

if page =="Remove":
    st.title('bhAIya - Remove products')
    
    with st.form(key='delete_item_form'):
        delete_id = st.text_input('ID to delete')
        submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            try:
                # Convert the ID to the appropriate type (int, if necessary)
                response = requests.post(base_url+"/removeOne", json={"id": int(delete_id)})
                
                if response.status_code == 200:
                    st.success('Item deleted successfully!')
                else:
                    st.error(f'Failed to delete item: {response.json().get("detail", "Unknown error")}')
            except ValueError:
                st.error("Invalid ID format. Please enter a numeric ID.")


st.write()
st.write()
st.write()
if page =="Products":
    st.title('bhAIya')
    items = list(collection_a.find())

    # Convert items to DataFrame
    df = pd.DataFrame(items)
    st.subheader('Item List')
    # Display first 10 items and allow scrolling for others
    st.dataframe(df.head(100), height=300)
