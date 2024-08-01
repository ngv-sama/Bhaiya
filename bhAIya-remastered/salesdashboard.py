# import streamlit as st
# import pymongo
# from pymongo import MongoClient
# import base64
# from PIL import Image
# from io import BytesIO
# import requests
# import pandas as pd

# from streamlit_navigation_bar import st_navbar

# page = st_navbar(["Home" ,"Add","Remove" ,"Products" ,"Sales","Customer details ","Support"])

# # st.logo("C:/Users/Administrator 1/Desktop/baby.jpg")

# ##08082A;
# ##extra colour replacement

# st.markdown(
#     """
#     <style>
#     [data-testid="stAppViewContainer"] > .main {
#         background-color: #000018;  /* Black background */
#         color: #fff;  /* White text */
#     }

#     [data-testid="stForm"] {
#         background-color: #fff;  /* White form background */
#         color: #000;  /* Black form text */
#     }

#     label, span,h1,h3{
#         color: #fff;  /* White text for headings, paragraphs, labels, spans, and list items */
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )
# if page =="Home":
#     st.title('bhAIya')
#     st.title('Seller Dashboard')

# # MongoDB connection
# client = MongoClient('localhost', 27017)
# db = client['bhAIya']
# collection_a = db['database']
# collection_i = db['imageDatabase']


# # Function to encode image to Base64
# def encode_image(image):
#     buffered = BytesIO()
#     image.save(buffered, format="JPEG")
#     return base64.b64encode(buffered.getvalue()).decode()

# # Function to decode Base64 to image
# def decode_image(encoded_image):
#     image_bytes = base64.b64decode(encoded_image)
#     return Image.open(BytesIO(image_bytes))

# # Streamlit app code
# #action = st.selectbox('Choose Action', ['Add Item', 'Delete Item', 'Upload Image',])


# base_url = "http://127.0.0.1:5004"


# import requests
# if page =="Add":
#     st.title('bhAIya - Add products')

#     actions = ['Select an action', 'Add Item','Upload Image']

#     # Use the selectbox with a default placeholder option
#     action = st.selectbox('Choose Action', actions)
#     # Add Item Form
#     if action == 'Add Item':
#         with st.form(key='add_item_form'):
#             new_id = st.text_input('ID')
#             new_masterCategory = st.text_input('Master Category')
#             new_sub_categories = st.text_input('Product Display Name')
#             new_additional_details = st.text_input('Additional Details')
#             new_price = st.text_input('Price')
#             submit_button = st.form_submit_button(label='Submit')

#             if submit_button:
#                 new_item = {
#                     'Main category': new_masterCategory.split(','),
#                     'Sub categories': new_sub_categories.split(','),
#                     'Additional details': new_additional_details.split(','),
#                     'id': int(new_id),
#                     'price': float(new_price),
#                 }
#                 response = requests.post(base_url+"/addOne", json={"data": new_item})
#                 if response.status_code == 200:
#                     st.success('Item added successfully!')
#                 else:
#                     st.error('Failed to add item.')

#     # Delete Item Form


#     # Upload Image Form
#     elif action == 'Upload Image':
#         with st.form(key='upload_image_form'):
#             image_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
#             image_id = st.text_input('Image ID')
#             submit_button = st.form_submit_button(label='Upload')

#             if submit_button and image_file:
#                 image = Image.open(image_file)
#                 encoded_image = encode_image(image)
#                 image_item = {

#                     'image': "b'"+ encoded_image,
#                     'id': int(image_id),
#                 }
#                 response = requests.post(base_url+"/addOne", json={"imgData": image_item})
#                 if response.status_code == 200:
#                     st.success('Image uploaded successfully!')
#                 else:
#                     st.error('Failed to upload image.')

# if page =="Remove":
#     st.title('bhAIya - Remove products')

#     with st.form(key='delete_item_form'):
#         delete_id = st.text_input('ID to delete')
#         submit_button = st.form_submit_button(label='Submit')

#         if submit_button:
#             try:
#                 # Convert the ID to the appropriate type (int, if necessary)
#                 response = requests.post(base_url+"/removeOne", json={"id": int(delete_id)})

#                 if response.status_code == 200:
#                     st.success('Item deleted successfully!')
#                 else:
#                     st.error(f'Failed to delete item: {response.json().get("detail", "Unknown error")}')
#             except ValueError:
#                 st.error("Invalid ID format. Please enter a numeric ID.")


# st.write()
# st.write()
# st.write()
# if page =="Products":
#     st.title('bhAIya')
#     items = list(collection_a.find())

#     # Convert items to DataFrame
#     df = pd.DataFrame(items)
#     st.subheader('Item List')
#     # Display first 10 items and allow scrolling for others
#     st.dataframe(df.head(100), height=300)

import streamlit as st
import pymongo
from pymongo import MongoClient
import base64
from PIL import Image
from io import BytesIO
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Custom CSS for a visually appealing dashboard
st.markdown(
    """
<style>
    /* Main container */
    .main {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #4CAF50;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Subheadings and labels */
    label, .stSelectbox label {
        color: #BDBDBD;
        font-weight: 500;
    }
    
    /* Forms */
    [data-testid="stForm"] {
        background-color: #2C2C2C;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #3C3C3C;
        color: #FFFFFF;
        border: 1px solid #4CAF50;
        border-radius: 5px;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #4CAF50;
        color: #FFFFFF;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #45a049;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    
    /* File uploader */
    .stFileUploader > div > button {
        background-color: #2196F3;
        color: #FFFFFF;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > button:hover {
        background-color: #1E88E5;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    
    /* Dataframe */
    .stDataFrame {
        border: 1px solid #4CAF50;
        border-radius: 5px;
    }
    
    /* Success and error messages */
    .stSuccess, .stError {
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
    }
    
    .stSuccess {
        background-color: rgba(76, 175, 80, 0.1);
        border: 1px solid #4CAF50;
    }
    
    .stError {
        background-color: rgba(244, 67, 54, 0.1);
        border: 1px solid #F44336;
    }

    /* Navbar styling */
    .navbar {
        display: flex;
        justify-content: space-between;
        padding: 10px;
        background-color: #2C2C2C;
        border-radius: 5px;
        margin-bottom: 20px;
    }

    .navbar-brand {
        color: #4CAF50;
        font-size: 24px;
        font-weight: bold;
        text-decoration: none;
    }

    .navbar-menu {
        display: flex;
        gap: 20px;
    }

    .navbar-item {
        color: #FFFFFF;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s ease;
    }

    .navbar-item:hover {
        color: #4CAF50;
    }
</style>
""",
    unsafe_allow_html=True,
)

# MongoDB connection
client = MongoClient("localhost", 27017)
db = client["bhAIya"]
collection_a = db["database"]
collection_i = db["imageDatabase"]

base_url = "http://127.0.0.1:5004"


# Function to encode image to Base64
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


# Function to decode Base64 to image
def decode_image(encoded_image):
    image_bytes = base64.b64decode(encoded_image)
    return Image.open(BytesIO(image_bytes))


# Custom navbar
def custom_navbar():
    st.markdown(
        """
    <div class="navbar">
        <a href="/" class="navbar-brand">bhAIya Dashboard</a>
        <div class="navbar-menu">
            <a href="/?page=add" class="navbar-item">Add</a>
            <a href="/?page=remove" class="navbar-item">Remove</a>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "home"

# Display the navbar
custom_navbar()

# Get the current page from the URL
page = st.experimental_get_query_params().get("page", ["home"])[0]

# Home page with placeholder charts
if page == "home":
    st.title("bhAIya Analytics Dashboard")

    # Placeholder metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Products", "1,234")
    with col2:
        st.metric("Total Categories", "15")
    with col3:
        st.metric("Average Price", "$49.99")

    # Placeholder chart: Product Category Distribution
    st.subheader("Product Category Distribution")
    categories = ["Electronics", "Clothing", "Home & Garden", "Books", "Toys"]
    values = [300, 250, 200, 150, 100]
    fig = px.pie(values=values, names=categories, title="Product Categories")
    st.plotly_chart(fig)

    # Placeholder chart: Price Distribution
    st.subheader("Price Distribution")
    price_ranges = ["$0-$25", "$26-$50", "$51-$100", "$101-$200", "$200+"]
    product_counts = [400, 300, 250, 200, 84]
    fig = px.bar(x=price_ranges, y=product_counts, title="Price Distribution")
    st.plotly_chart(fig)

    # Placeholder chart: Monthly Sales
    st.subheader("Monthly Sales")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    sales = [5000, 6000, 7500, 8000, 8500, 9000]
    fig = px.line(x=months, y=sales, title="Monthly Sales Trend")
    st.plotly_chart(fig)

    # Placeholder: Recent Products
    st.subheader("Recent Products")
    recent_products = pd.DataFrame(
        {
            "ID": [1001, 1002, 1003, 1004, 1005],
            "Product Name": [
                "Smartphone",
                "T-shirt",
                "Garden Hose",
                "Novel",
                "Action Figure",
            ],
            "Category": ["Electronics", "Clothing", "Home & Garden", "Books", "Toys"],
            "Price": [599.99, 19.99, 29.99, 14.99, 24.99],
        }
    )
    st.dataframe(recent_products)

# Add page (kept the same as the original code)
elif page == "add":
    st.title("Add Products")

    actions = ["Select an action", "Add Item", "Upload Image"]
    action = st.selectbox("Choose Action", actions)

    if action == "Add Item":
        with st.form(key="add_item_form"):
            new_id = st.text_input("ID")
            new_masterCategory = st.text_input("Master Category")
            new_sub_categories = st.text_input("Product Display Name")
            new_additional_details = st.text_input("Additional Details")
            new_price = st.text_input("Price")
            submit_button = st.form_submit_button(label="Submit")

            if submit_button:
                new_item = {
                    "Main category": new_masterCategory.split(","),
                    "Sub categories": new_sub_categories.split(","),
                    "Additional details": new_additional_details.split(","),
                    "id": int(new_id),
                    "price": float(new_price),
                }
                response = requests.post(base_url + "/addOne", json={"data": new_item})
                if response.status_code == 200:
                    st.success("Item added successfully!")
                else:
                    st.error("Failed to add item.")

    elif action == "Upload Image":
        with st.form(key="upload_image_form"):
            image_file = st.file_uploader(
                "Choose an image...", type=["jpg", "jpeg", "png"]
            )
            image_id = st.text_input("Image ID")
            submit_button = st.form_submit_button(label="Upload")

            if submit_button and image_file:
                image = Image.open(image_file)
                encoded_image = encode_image(image)
                image_item = {
                    "image": "b'" + encoded_image,
                    "id": int(image_id),
                }
                response = requests.post(
                    base_url + "/addOne", json={"imgData": image_item}
                )
                if response.status_code == 200:
                    st.success("Image uploaded successfully!")
                else:
                    st.error("Failed to upload image.")

# Remove page (kept the same as the original code)
elif page == "remove":
    st.title("Remove Products")

    with st.form(key="delete_item_form"):
        delete_id = st.text_input("ID to delete")
        submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            try:
                response = requests.post(
                    base_url + "/removeOne", json={"id": int(delete_id)}
                )

                if response.status_code == 200:
                    st.success("Item deleted successfully!")
                else:
                    st.error(
                        f'Failed to delete item: {response.json().get("detail", "Unknown error")}'
                    )
            except ValueError:
                st.error("Invalid ID format. Please enter a numeric ID.")

# Footer
st.markdown("---")
st.markdown("© 2024 bhAIya Seller Dashboard. All rights reserved.")
