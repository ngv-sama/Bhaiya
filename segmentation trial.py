import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymongo
from pymongo import MongoClient
import numpy as np
import plotly.express as px
from mpl_toolkits.mplot3d import Axes3D

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['segmenttrial']
collection = db['segt']

# Function to load data from MongoDB
def load_data():
    data = list(collection.find())
    df = pd.DataFrame(data)
    # Convert product_tags from list to a string
    df['product_tags'] = df['product_tags'].apply(lambda x: ', '.join(x))
    # Ensure columns are properly named and typed
    df.columns = [col.lower() for col in df.columns]
    return df

# Load data
df = load_data()

# Add a mock 'cluster' column for demonstration
df['cluster'] = np.random.choice(['High', 'Medium', 'Low'], size=len(df))

# Streamlit app
st.title('Customer Clustering Visualizations')

# Buttons for different types of clustering
option = st.sidebar.selectbox(
    'Select Clustering Type',
    ['Value-Based Clustering', 'Product Interest Clustering', 'RFM Clustering',
     'Discount Sensitivity Clustering', 'Geo-Location-Based Clustering', 
     'Purchase Frequency-Based Clustering', 'Behavioral Clustering', 'Combination Clustering']
)

# Visualizations
if option == 'Value-Based Clustering':
    st.header('Value-Based Clustering')
    st.subheader('Scatter Plot of Avg Purchase Value vs Purchase Frequency')
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x='avg_purchase_value', y='purchase_frequency', hue='cluster', data=df, palette='viridis', ax=ax)
        ax.set_title('Value-Based Clustering')
        ax.set_xlabel('Average Purchase Value')
        ax.set_ylabel('Purchase Frequency')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error: {e}")

elif option == 'Product Interest Clustering':
    st.header('Product Interest Clustering')
    st.subheader('Bar Chart of Product Categories')
    try:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.countplot(x='product_category', hue='cluster', data=df, ax=ax)
        ax.set_title('Product Interest Clustering')
        ax.set_xlabel('Product Category')
        ax.set_ylabel('Count')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error: {e}")

elif option == 'RFM Clustering':
    st.header('Recency-Frequency-Monetary (RFM) Clustering')
    st.subheader('3D Scatter Plot')
    try:
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        scatter = ax.scatter(df['purchase_recency'], df['purchase_frequency'], df['avg_purchase_value'], c=df['cluster'].astype('category').cat.codes)
        ax.set_xlabel('Purchase Recency')
        ax.set_ylabel('Purchase Frequency')
        ax.set_zlabel('Average Purchase Value')
        plt.title('RFM Clustering')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error: {e}")

elif option == 'Discount Sensitivity Clustering':
    st.header('Discount Sensitivity Clustering')
    st.subheader('Box Plot of Avg Purchase Value by Discount Usage')
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(x='discount_usage', y='avg_purchase_value', data=df, ax=ax)
        ax.set_title('Discount Sensitivity Clustering')
        ax.set_xlabel('Discount Usage')
        ax.set_ylabel('Average Purchase Value')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error: {e}")

elif option == 'Geo-Location-Based Clustering':
    st.header('Geo-Location-Based Clustering')
    st.subheader('Scatter Plot of Geo-Location vs Avg Purchase Value')
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.scatterplot(x='geo_location', y='avg_purchase_value', hue='cluster', data=df, ax=ax)
        ax.set_title('Geo-Location Based Clustering')
        ax.set_xlabel('Geo Location')
        ax.set_ylabel('Average Purchase Value')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error: {e}")

elif option == 'Purchase Frequency-Based Clustering':
    st.header('Purchase Frequency-Based Clustering')
    st.subheader('Histogram of Purchase Frequency')
    try:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.histplot(data=df, x='purchase_frequency', hue='cluster', multiple='stack', palette='tab10', ax=ax)
        ax.set_title('Purchase Frequency-Based Clustering')
        ax.set_xlabel('Purchase Frequency')
        ax.set_ylabel('Count')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error: {e}")

elif option == 'Behavioral Clustering':
    st.header('Behavioral Clustering')
    st.subheader('Pair Plot of Purchase Frequency and Recency')
    try:
        # Only use numerical data for pairplot
        fig = sns.pairplot(df[['purchase_frequency', 'purchase_recency', 'cluster']], hue='cluster')
        plt.title('Behavioral Clustering')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error: {e}")

elif option == 'Combination Clustering':
    st.header('Combination Clustering')
    st.subheader('Heatmap of Avg Purchase Value by Product Category and Geo-Location')
    try:
        heatmap_data = df.pivot_table(index='geo_location', columns='product_category', values='avg_purchase_value', aggfunc='mean')
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(heatmap_data, cmap='YlGnBu', annot=True, ax=ax)
        ax.set_title('Combination Clustering Heatmap')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error: {e}")
