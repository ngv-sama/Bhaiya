import streamlit as st
import pandas as pd
import numpy as np

# Dummy sidebar
st.sidebar.title("Navigation")
st.sidebar.markdown("### Pages")
st.sidebar.radio("Go to", ["Sales", "Orders", "Inventory", "Customers"])

# Background image
background_image = """
<style>
[data-testid="stAppViewContainer"] > .main {
    background-image: url("https://hougumlaw.com/wp-content/uploads/2016/05/light-website-backgrounds-light-color-background-images-light-color-background-images-for-website-1024x640.jpg");
    background-size: 100vw 100vh;  # This sets the size to cover 100% of the viewport width and height
    background-position: center;  
    background-repeat: no-repeat;
}
</style>
"""

st.markdown(background_image, unsafe_allow_html=True)

# Read the CSV file
df = pd.read_csv('database.csv')

# Display the first 10 items in a table with scroll functionality
st.title('Seller Dashboard')
st.subheader('Item List')
st.dataframe(df[['id', 'masterCategory', 'productDisplayName', 'price']].head(100))

# Add or Delete Item
st.subheader('Manage Items')
action = st.selectbox('Select Action', ['Add Item', 'Delete Item'])

if action == 'Add Item':
    if st.button('Add Item'):
        with st.form(key='add_item_form'):
            new_id = st.text_input('ID')
            new_masterCategory = st.text_input('Master Category')
            new_productDisplayName = st.text_input('Product Display Name')
            new_price = st.text_input('Price')
            submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            new_item = {
                'id': new_id,
                'masterCategory': new_masterCategory,
                'productDisplayName': new_productDisplayName,
                'price': new_price
            }
            df = df.append(new_item, ignore_index=True)
            df.to_csv('database.csv', index=False)
            st.success('Item added successfully!')

elif action == 'Delete Item':
    if st.button('Delete Item'):
        delete_id = st.text_input('Enter ID of item to delete')
        delete_button = st.button('Confirm Delete')

        if delete_button:
            df = df[df['id'] != delete_id]
            df.to_csv('database.csv', index=False)
            st.success('Item deleted successfully!')

# Buyer Analytics
st.sidebar.subheader('Buyer Analytics')
# Generate random data for analytics
sales_data = df.copy()
sales_data['sales'] = np.random.randint(1, 100, size=len(df))

# Display highest sales item in sidebar
highest_sales_item = sales_data.loc[sales_data['sales'].idxmax()]
st.sidebar.write(f"Highest Sales Item: {highest_sales_item['productDisplayName']} with {highest_sales_item['sales']} sales")

# Display a bar chart of sales in sidebar
st.sidebar.bar_chart(sales_data[['productDisplayName', 'sales']].set_index('productDisplayName'))

# Display highest sales item at the bottom of the main content area
st.subheader('Highest Sales Item')
st.write(f"Highest Sales Item: {highest_sales_item['productDisplayName']} with {highest_sales_item['sales']} sales")

# Display a bar chart of sales at the bottom of the main content area
st.subheader('Sales Bar Chart')
st.bar_chart(sales_data[['productDisplayName', 'sales']].set_index('productDisplayName'))