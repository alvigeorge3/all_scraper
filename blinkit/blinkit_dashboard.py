import streamlit as st
import pandas as pd
import plotly.express as px
import os
import glob

# Page Config
st.set_page_config(
    page_title="Blinkit Analytics (Local)",
    page_icon="🟡",
    layout="wide"
)

st.title("🟡 Blinkit Analytics")

# Load env vars
from dotenv import load_dotenv
load_dotenv()

from database import db

# Load Data
@st.cache_data(ttl=60)
def load_data():
    df_db = pd.DataFrame()
    df_csv = pd.DataFrame()
    
    # 1. Try Loading from Supabase
    if db.client:
        try:
            response = db.client.table("products").select("*").eq("platform", "blinkit").execute()
            df_db = pd.DataFrame(response.data)
            if not df_db.empty:
                st.toast("✅ Data loaded from Supabase")
        except Exception as e:
            st.warning(f"Supabase connection error: {e}")

    # 2. Try Loading from Local CSV (Fallback)
    files = glob.glob("blinkit_*.csv")
    if files:
        latest_file = max(files, key=os.path.getctime)
        try:
            df_csv = pd.read_csv(latest_file)
            df_csv.columns = [c.lower() for c in df_csv.columns]
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    # Combine or Select Source
    if not df_db.empty:
        return df_db
    elif not df_csv.empty:
        st.caption(f"⚠️ Using local CSV backup: `{latest_file}`")
        return df_csv
    else:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No Blinkit data found in Supabase or local CSVs.")
    st.info("Run `upload_blinkit_data.py` to sync CSV data to Supabase.")
    st.stop()

# Filters
if 'category' in df.columns:
    st.sidebar.header("Filters")
    categories = st.sidebar.multiselect("Category", df['category'].unique(), default=df['category'].unique())
    df = df[df['category'].isin(categories)]

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Products", len(df))
if 'price' in df.columns: col2.metric("Avg Price", f"₹{df['price'].mean():.2f}")
if 'eta' in df.columns:
    try:
        avg_mins = df['eta'].str.extract(r'(\d+)').astype(float).mean().iloc[0]
        col3.metric("Avg ETA", f"{avg_mins:.0f} mins")
    except: col3.metric("Avg ETA", "N/A")
if 'discount' in df.columns: col4.metric("Avg Discount", f"{df['discount'].mean():.1f}%")

# Tabs
tab1, tab2 = st.tabs(["📊 Analytics", "📝 Data Grid"])

with tab1:
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        if 'price' in df.columns:
            st.subheader("Price Distribution")
            fig_price = px.histogram(df, x="price", nbins=20, title="Price Distribution", color_discrete_sequence=['#F1C40F'])
            st.plotly_chart(fig_price, use_container_width=True)
    with col_chart2:
        if 'category' in df.columns:
            st.subheader("Category Share")
            fig_pie = px.pie(df, names="category", title="Product Count by Category", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader("Product Details")
    column_config = {}
    if 'image_url' in df.columns:
        column_config["image_url"] = st.column_config.ImageColumn("Image", width="small")
    url_col = 'product_url' if 'product_url' in df.columns else 'url'
    if url_col in df.columns:
        column_config[url_col] = st.column_config.LinkColumn("Link")
    
    st.dataframe(df, column_config=column_config, use_container_width=True, hide_index=True, height=600)
