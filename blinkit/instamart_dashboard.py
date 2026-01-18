import streamlit as st
import pandas as pd
import plotly.express as px
import os
import glob

# Page Config
st.set_page_config(
    page_title="Instamart Analytics (Local)",
    page_icon="🟠",
    layout="wide"
)

st.title("🟠 Instamart Analytics")

# Load Data from CSV
@st.cache_data(ttl=60)
def load_data():
    # Look for the latest available CSV
    files = glob.glob("instamart_*.csv")
    if not files:
        return pd.DataFrame()
        
    # Use the most recent file
    latest_file = max(files, key=os.path.getctime)
    st.caption(f"Loading data from: `{latest_file}`")
    
    try:
        df = pd.read_csv(latest_file)
        if not df.empty:
            # Normalize column names if needed
            df.columns = [c.lower() for c in df.columns]
            
            # Numeric conversion
            if 'price' in df.columns:
                df['price'] = pd.to_numeric(df['price'], errors='coerce')
            if 'mrp' in df.columns:
                df['mrp'] = pd.to_numeric(df['mrp'], errors='coerce')
            
            # Calculate discount if possible
            if 'price' in df.columns and 'mrp' in df.columns:
                df['discount'] = ((df['mrp'] - df['price']) / df['mrp'] * 100).round(1)
                
        return df
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data found in Instamart CSV files.")
    st.info("Please run `run_instamart_assortment.py` or `run_instamart_availability.py` first.")
    st.stop()

# Filter Data (Category only if exists)
if 'category' in df.columns:
    st.sidebar.header("Filters")
    categories = st.sidebar.multiselect("Category", df['category'].unique(), default=df['category'].unique())
    df = df[df['category'].isin(categories)]

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Products", len(df))

if 'price' in df.columns:
    col2.metric("Avg Price", f"₹{df['price'].mean():.2f}")

if 'eta' in df.columns:
    try:
        # Extract numeric minutes
        avg_mins = df['eta'].str.extract(r'(\d+)').astype(float).mean().iloc[0]
        col3.metric("Avg ETA", f"{avg_mins:.0f} mins")
    except:
        col3.metric("Avg ETA", "N/A")

if 'discount' in df.columns:
    col4.metric("Avg Discount", f"{df['discount'].mean():.1f}%")

# Tabs
tab1, tab2 = st.tabs(["📊 Analytics", "📝 Data Grid"])

with tab1:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        if 'price' in df.columns:
            st.subheader("Price Distribution")
            fig_price = px.histogram(df, x="price", nbins=20, title="Price Distribution", color_discrete_sequence=['#E67E22'])
            st.plotly_chart(fig_price, use_container_width=True)
        
    with col_chart2:
        if 'category' in df.columns:
            st.subheader("Category Share")
            fig_pie = px.pie(df, names="category", title="Product Count by Category", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader("Product Details")
    
    # Configure Columns
    column_config = {}
    if 'image_url' in df.columns:
        column_config["image_url"] = st.column_config.ImageColumn("Image", width="small")
    if 'product_url' in df.columns or 'url' in df.columns:
        url_col = 'product_url' if 'product_url' in df.columns else 'url'
        column_config[url_col] = st.column_config.LinkColumn("Link")
    if 'price' in df.columns:
        column_config["price"] = st.column_config.NumberColumn("Price", format="₹%d")
    
    st.dataframe(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        height=600
    )

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
