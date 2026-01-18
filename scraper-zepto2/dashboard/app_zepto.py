import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess
import sys
import os

# Add parent directory to path to import database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database

st.set_page_config(page_title="Zepto Analytics Dashboard", layout="wide")

st.title("🛍️ Zepto Assortment & Availability Dashboard")

# Initialize DB
@st.cache_resource
def get_db():
    return Database()

db = get_db()
if not db.client:
    st.error("❌ Database connection failed. Please check your `.env` file credentials.")
    st.stop()

# Fetch Data
@st.cache_data(ttl=600)
def load_data():
    data = db.fetch_products(limit=2000)
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    
    # Ensure numeric columns
    for col in ['price', 'mrp', 'inventory']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # Process Dates
    if 'scraped_at' in df.columns:
        df['scraped_at'] = pd.to_datetime(df['scraped_at'])
        # Create a formatted string for the filter (dd-mm-yyyy HH:MM:SS)
        df['scrape_time_str'] = df['scraped_at'].dt.strftime('%d-%m-%Y %H:%M:%S')
        df['date'] = df['scraped_at'].dt.date
    
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['created_time_str'] = df['created_at'].dt.strftime('%d-%m-%Y %H:%M:%S')
            
    return df

with st.spinner("Loading data from Supabase..."):
    df = load_data()

if df.empty:
    st.warning("No data found in database. Run scraper or upload data first.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Filters")

# Time Filters
if 'scrape_time_str' in df.columns:
    available_times = sorted(df['scrape_time_str'].unique(), reverse=True)
    scrape_time_filter = st.sidebar.multiselect("Select Scrape Time", options=available_times, default=available_times[:1])
else:
    scrape_time_filter = []

if 'created_time_str' in df.columns:
    available_created = sorted(df['created_time_str'].unique(), reverse=True)
    created_time_filter = st.sidebar.multiselect("Select DB Upload Time", options=available_created)
else:
    created_time_filter = []

pincode_filter = st.sidebar.multiselect("Select Pincode", options=df['pincode_input'].unique())
category_filter = st.sidebar.multiselect("Select Category", options=df['category'].dropna().unique())

st.sidebar.markdown("---")
st.sidebar.header("🚀 Scraper Controls")

# Mode Selection
scrape_mode = st.sidebar.radio("Select Scrape Mode", ["Assortment (All Categories)"])

if scrape_mode == "Assortment (All Categories)":
    uploaded_file = st.sidebar.file_uploader("Upload Pincodes Excel", type=['xlsx'], key="assortment_uploader")
    if uploaded_file is not None:
        try:
            # Save to parent directory
            file_path = os.path.join(os.path.dirname(__file__), '..', 'pin_codes.xlsx')
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.sidebar.success("✅ Saved as pin_codes.xlsx")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
            
    if st.sidebar.button("Run Assortment Scraper"):
        script_path = os.path.join(os.path.dirname(__file__), '..', 'run_zepto_assortment_parallel.py')
        if not os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'pin_codes.xlsx')):
             st.sidebar.error("pin_codes.xlsx not found!")
        else:
            subprocess.Popen([sys.executable, script_path], 
                             cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
            st.sidebar.success("Assortment Scraper started!")

filtered_df = df.copy()

# Apply Filters
if scrape_time_filter:
    filtered_df = filtered_df[filtered_df['scrape_time_str'].isin(scrape_time_filter)]
if created_time_filter:
    filtered_df = filtered_df[filtered_df['created_time_str'].isin(created_time_filter)]
    
if pincode_filter:
    filtered_df = filtered_df[filtered_df['pincode_input'].isin(pincode_filter)]
if category_filter:
    filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Products", len(filtered_df))
col2.metric("Avg Price", f"₹{filtered_df['price'].mean():.2f}")
out_of_stock = len(filtered_df[filtered_df['availability'] == 'Out of Stock'])
col3.metric("Out of Stock", out_of_stock, delta_color="inverse")
col4.metric("Categories", filtered_df['category'].nunique())

# Charts
st.subheader("📊 Analytics")
c1, c2 = st.columns(2)

with c1:
    st.markdown("### Availability Status")
    fig_avail = px.pie(filtered_df, names='availability', title="In Stock vs Out of Stock", hole=0.4)
    st.plotly_chart(fig_avail, use_container_width=True)

with c2:
    st.markdown("### Price Distribution")
    fig_price = px.histogram(filtered_df, x='price', nbins=30, title="Price Distribution", color_discrete_sequence=['#4CAF50'])
    st.plotly_chart(fig_price, use_container_width=True)

# Data Grid
st.subheader("📋 Raw Data Explorer")
search_term = st.text_input("Search Product Name", "")
if search_term:
    filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False, na=False)]

st.dataframe(filtered_df, use_container_width=True)
