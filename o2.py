import streamlit as st
import pandas as pd
import numpy as np

st.sidebar.radio("Go to", ["Sales", "Orders", "Inventory", "Customers"])

# Background image and custom styles
custom_styles = """
<style>
[data-testid="stAppViewContainer"] > .main {
    background-color: #000;  /* Black background */
    color: #fff;  /* White text */
}





h1, h2, h3, h4, h5, h6 {
    color: #fff;  /* White headings */
}

p, label {
    color: #333;  /* Dark Gray text */
}

input[type="text"], input[type="password"], textarea {
    background-color: #f2f2f2;  /* Very light gray input background */
    border: 1px solid #ccc;  /* Light Gray border */
}

input[type="text"]:focus, input[type="password"]:focus, textarea:focus {
    background-color: #f2f2f2;  /* Very light gray input background on focus */
    border-color: #555;  /* Light Blue border on focus */
}

button {
    background-color: #333;  /* Dark Gray button background */
    color: #fff;  /* White button text */
}

button:hover {
    background-color: #555;  /* Light Blue button background on hover */
}

.scrollbar-thumb {
    background-color: #888;  /* Gray scrollbar thumb */
}

.scrollbar-thumb:hover {
    background-color: #555;  /* Light Blue scrollbar thumb on hover */
}
</style>
"""

st.markdown(custom_styles, unsafe_allow_html=True)

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
elif action == 'Delete Item':
    if st.button('Delete Item'):
        delete_id = st.text_input('Enter ID of item to delete')
        delete_button = st.button('Confirm Delete')

        if delete_button:
            df = df[df['id'] != delete_id]
            df.to_csv('database.csv', index=False)
            st.success('Item deleted successfully!')

# Buyer Analytics
st.sidebar.header('Buyer Analytics')
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
