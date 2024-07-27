import streamlit as st
from streamlit_card import card
import pandas as pd
from PIL import Image
import io
import requests
import base64


BACKEND_URL = "http://127.0.0.1:8000/data"

# Initialize item details to ensure it is correctly handled across sessions
if 'item_details' not in st.session_state:
    st.session_state['item_details'] = {}

def recomms(desc, image=None):
    # Placeholder for ML model code
    # Return dummy data for now
    print("data for the API: ",desc,image[:10] if image else None)
    with st.spinner("Fetching recommendations..."):
        try:
            data=requests.post(BACKEND_URL,json={"text":desc,"img64":image})
            if data.ok:
                data=data.json()
                # return [{"id":key,**value} for key,value in data.items()]
            return data
        except Exception as e:
            print("error in API call ---",e)
    
    # return [
    #         {
    #             "id": 15970,
    #             "Main category": ["Men's Apparel", "Shirts", "Apparel", "Tops"],
    #             "Sub categories": ["Shirt", "Plaid", "Casual Wear"],
    #             "Additional details": ["Fll 2011.0", "Turtle Check", "Navy Blue"],
    #             "price": 70461,
    #             "image": "b'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'"
    #         },
    #         {
    #             "id": 39386,
    #             "Main category": ["Men's Apparel", "Bottomwear", "Clothing"],
    #             "Sub categories": ["Jeans"],
    #             "Additional details": ["Summer 2012.0", "Blue", "Casual", "Party"],
    #             "price": 10378,
    #             "image": "b'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'"
    #         }
    # ]
        

def addcatalog(details):
    # Placeholder for catalog addition code
    pass

def item_page(details):
    st.header('Item Details')
    st.image(base64.b64decode(details['image'].removeprefix("b'").removesuffix("'").encode()))
    st.write(f"Price: {details['price']}")
    # st.write(f"Store: {details['store']}")
    if st.button('Back'):
            st.session_state['page'] = 'customer'
            st.rerun()
    # if st.button('Home'):
    #     st.session_state['page'] = 'landing'
    #     st.rerun()


def customer_page():
    # st.header('Customer Section')
    # if st.button("Home"):
    #     st.session_state["page"] = "landing"
    #     st.rerun()
    desc = st.text_area('Description')
    uploaded_image = None
    taken_image = None

    uploaded_image = st.file_uploader('Upload an optional picture', type=['jpg', 'png'])
    st.write(f"{'-'*68}OR{'-'*69}")
    if(st.button("Take a photo")):
        taken_image = st.camera_input("Take a picture")

    if taken_image is not None:
        uploaded_image = taken_image
        print(uploaded_image)

    if st.button("Get Recommendations"):
        if desc or uploaded_image:
            if uploaded_image:
                image = Image.open(uploaded_image)
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                image_data = buffered.getvalue()
                image = base64.b64encode(image_data).decode()
            else:
                image = None

            desc = desc if desc else None
            recs = recomms(desc, image)
            st.session_state["recommendations"] = recs
    # todo price range

    # if st.button("Home"):
    #     st.session_state["page"] = "landing"
    #     st.rerun()

    # if st.button('Get Recommendations'):
    #     if desc or uploaded_image:
    #         if uploaded_image:
    #             image = Image.open(uploaded_image)
    #             buffered = io.BytesIO()
    #             image.save(buffered, format="PNG")
    #             image_data = buffered.getvalue()
    #             image = base64.b64encode(image_data).decode()
    #         else:
    #             image = None

    #         desc=desc if desc else None
    #         recs = recomms(desc, image)
    #         st.session_state['recommendations'] = recs

    if 'recommendations' in st.session_state:
        recs = st.session_state['recommendations']
        for idx, rec in enumerate(recs):
            theimage=base64.b64decode(rec['image'].removeprefix("b'").removesuffix("'").encode())
            container = st.container()
            with container:
                col1, col2 = st.columns(2)
                with col1:
                    st.image(theimage, use_column_width=True)
                with col2:
                    st.write(f"Price: {rec['price']}")
                    st.write(f"Location: {rec['id']}")
                    if st.button('View', key=f"view_{idx}"):
                        st.session_state['item_details'] = rec
                        st.session_state['page'] = 'item'
                        st.rerun()


# def retailer_page():
#     st.header('Retailer Section')
#     if 'authenticated' not in st.session_state:
#         st.session_state['authenticated'] = False

#     if not st.session_state['authenticated']:
#         password = st.text_input('Enter password', type='password')
#         if st.button('Login'):
#             if password == 'your_password':
#                 st.session_state['authenticated'] = True
#             else:
#                 st.error('Invalid password')

#         if st.button('Home'):
#             st.session_state['page'] = 'landing'
#             st.rerun()
#         if st.button('Customer'):
#             st.session_state['page'] = 'customer'
#             st.rerun()
#     else:
#         option = st.selectbox('Select option', ['Add Item', 'Edit Item', 'Delete Item'])

#         if option == 'Add Item':
#             item_name = st.text_input('Item Name')
#             item_description = st.text_area('Item Description')
#             item_maincategory = st.text_input('Item Category (give comma seperated values)')
#             item_subcategory = st.text_area('Item Sub Category (give comma seperated values)')
#             item_addedcategory = st.text_area('Item Additional Categories (give comma seperated values)')
#             item_price = st.number_input('Price', min_value=0.0, format="%.2f")
#             item_quantity = st.number_input('Quantity', min_value=0)
#             item_image = st.file_uploader('Upload item picture', type=['jpg', 'png'])
#             item_location = st.text_input('Item Location')

#             if st.button('Add Item'):
#                 if item_image:
#                     image_bytes = item_image.read()
#                     image = Image.open(io.BytesIO(image_bytes))
#                     dets = {
#                         'name': item_name,
#                         'description': item_description,
#                         'Main category': item_maincategory.split(','),
#                         'Sub categories':item_subcategory.split(','),
#                         'Additional details':item_addedcategory.split(','),
#                         'price': int(item_price),
#                         'quantity': item_quantity,
#                         'image': image,
#                         # 'store': item_location
#                     }
#                     addcatalog(dets)
#                     st.success('Item added to catalog')

#         elif option == 'Edit Item':
#             item_id = st.text_input('Enter Item ID to edit')
#             if st.button('Edit'):
#                 edit_item(item_id)

#         elif option == 'Delete Item':
#             item_id = st.text_input('Enter Item ID to delete')
#             num_items = st.number_input('Enter number of items to delete', min_value=1)
#             if st.button('Delete'):
#                 delete_item(item_id, num_items)

#         if st.button('Home'):
#             st.session_state['page'] = 'landing'
#             st.rerun()


# Landing Page
st.title('bhAIya : Find your product today')
st.header("Hello there! What are you looking for today?")

if 'page' not in st.session_state:
    st.session_state['page'] = 'landing'

if st.session_state['page'] == 'landing':
    st.session_state['page'] = 'customer'
    st.rerun()
    # if st.button('Retailer'):
    #     st.session_state['page'] = 'retailer'
    #     st.rerun()


if st.session_state['page'] == 'item':
    item_page(st.session_state['item_details'])
elif st.session_state['page'] == 'customer':
    customer_page()
# elif st.session_state['page'] == 'retailer':
#     retailer_page()
