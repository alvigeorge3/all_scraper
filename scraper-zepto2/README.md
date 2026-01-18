# 🛒 Zepto Scraper

A robust, automated web scraping solution for extracting product assortment data from Zepto's e-commerce platform. Features parallel execution, Supabase cloud storage, and an interactive Streamlit analytics dashboard.

## 🌟 Features

- **Multi-Pincode Scraping**: Process multiple pincodes in parallel for efficient data collection
- **Comprehensive Data Extraction**: Captures 20+ fields including price, MRP, inventory, ETA, shelf life, and more
- **Anti-Bot Measures**: Stealth browser automation with human-like behaviors
- **Cloud Storage**: Automatic upload to Supabase (PostgreSQL)
- **Analytics Dashboard**: Interactive Streamlit UI with filters, charts, and metrics
- **Historical Tracking**: Maintains scrape history for trend analysis

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Supabase account (free tier available at https://supabase.com)

## 🚀 Installation

### 1. Clone or Download

```bash
cd c:\scrapers\scraper-zepto2
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers

```bash
playwright install chromium
```

### 4. Configure Supabase

1. Create a Supabase project at https://supabase.com
2. Copy `.env.template` to `.env`:
   ```bash
   copy .env.template .env
   ```
3. Edit `.env` and add your credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key-here
   ```

4. Create the `zepto_products` table in Supabase SQL Editor:

```sql
CREATE TABLE zepto_products (
    id BIGSERIAL PRIMARY KEY,
    platform TEXT NOT NULL,
    category TEXT,
    subcategory TEXT,
    clicked_label TEXT,
    name TEXT,
    brand TEXT,
    base_product_id TEXT,
    product_id TEXT,
    store_id TEXT,
    group_id TEXT,
    merchant_type TEXT,
    mrp DOUBLE PRECISION,
    price DOUBLE PRECISION,
    weight TEXT,
    shelf_life_in_hours INTEGER,
    eta TEXT,
    availability TEXT,
    inventory INTEGER,
    scraped_at TIMESTAMP,
    pincode_input TEXT,
    product_url TEXT,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_zepto_pincode ON zepto_products(pincode_input);
CREATE INDEX idx_zepto_category ON zepto_products(category);
CREATE INDEX idx_zepto_scraped_at ON zepto_products(scraped_at);
```

## 📖 Usage

### Single Pincode Scraping

Scrape all categories for a specific pincode:

```bash
python run_zepto_assortment.py --pincode 560001
```

**Options:**
- `--pincode`: 6-digit pincode (default: 560001)
- `--headless`: Run in headless mode (no browser window)

**Output:** `zepto_assortment_YYYYMMDD_HHMMSS.csv`

### Multi-Pincode Parallel Scraping

Process multiple pincodes simultaneously for faster collection:

1. Prepare `pin_codes.xlsx` with a `Pincode` column
2. Run the parallel scraper:

```bash
python run_zepto_assortment_parallel.py
```

**Configuration:**
- Edit `MAX_WORKERS` in the script (default: 4 parallel workers)

**Output:** `zepto_assortment_parallel_YYYYMMDD_HHMMSS.csv`

### Upload to Supabase

Upload scraped CSV data to your Supabase database:

```bash
python upload_zepto_data.py --file zepto_assortment_20260118_120000.csv
```

**Options:**
- `--file`: Path to CSV file (required)
- `--table`: Table name (default: zepto_products)

### Analytics Dashboard

Launch the interactive Streamlit dashboard:

```bash
streamlit run dashboard/app_zepto.py
```

**Dashboard Features:**
- **Filters**: Time, pincode, category, availability
- **Metrics**: Total products, avg price, out-of-stock count
- **Charts**: Availability pie chart, price distribution
- **Scraper Controls**: Upload pincodes and trigger scraper from UI
- **Search**: Find products by name

Access at: http://localhost:8501

## 📊 Data Fields

Each product record contains:

| Field | Description |
|-------|-------------|
| `platform` | Always "zepto" |
| `category` | Primary category |
| `subcategory` | Product subcategory |
| `clicked_label` | Navigation path |
| `name` | Product name |
| `brand` | Brand name |
| `base_product_id` | Unique product ID |
| `product_id` | Product identifier |
| `store_id` | Store/merchant ID |
| `mrp` | Maximum Retail Price |
| `price` | Selling price |
| `weight` | Pack size (e.g., "1 kg") |
| `shelf_life_in_hours` | Product shelf life |
| `eta` | Delivery ETA (minutes) |
| `availability` | In Stock / Out of Stock |
| `inventory` | Available quantity |
| `scraped_at` | Scrape timestamp |
| `pincode_input` | Input pincode |
| `product_url` | Product page URL |
| `image_url` | Product image URL |

## 🔧 Troubleshooting

### Browser Launch Issues

If Playwright can't launch browsers:
```bash
playwright install chromium --force
```

### Supabase Connection Errors

- Verify credentials in `.env` file
- Check Supabase project status
- Ensure table schema is created

### No Products Found

- Zepto's selectors may have changed (update selectors in `scrapers/zepto.py`)
- Location setting might have failed (check logs)
- Try running in non-headless mode to debug: remove `--headless` flag

### Anti-Bot Detection

- Increase delays in `base.py` (`human_delay` values)
- Reduce `MAX_WORKERS` to decrease request rate
- Run scrapers during off-peak hours

## 📁 Project Structure

```
scraper-zepto2/
├── scrapers/
│   ├── __init__.py
│   ├── base.py           # Base scraper with anti-bot features
│   ├── models.py         # Data models
│   └── zepto.py          # Zepto-specific logic
├── dashboard/
│   └── app_zepto.py      # Streamlit dashboard
├── database.py           # Supabase client
├── run_zepto_assortment.py          # Single-pincode runner
├── run_zepto_assortment_parallel.py # Parallel runner
├── upload_zepto_data.py  # CSV uploader
├── requirements.txt      # Dependencies
├── .env.template         # Environment template
├── pin_codes.xlsx        # Input pincodes
└── README.md            # This file
```

## 🤝 Contributing

This scraper is based on the Blinkit scraper architecture. For improvements:

1. Update selectors in `scrapers/zepto.py` if website structure changes
2. Adjust `human_delay` values for rate limiting
3. Add new features to the dashboard

## 📄 License

This project is for educational and research purposes only. Please respect Zepto's Terms of Service and robots.txt when scraping.

## 🙏 Acknowledgments

Based on the proven architecture from the Blinkit scraper project.
