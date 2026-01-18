import csv
from scrapers.models import ProductItem
from typing import get_type_hints

def generate_schema_csv():
    # Get keys from the TypedDict
    # Note: TypedDict keys are not directly accessible as list in older python versions easily without instantiation
    # But we can assume standard fields or instantiate a dummy
    
    dummy_item: ProductItem = {
        "platform": "zepto",
        "category": "Masala & Dry Fruits",
        "subcategory": "Dry Fruits",
        "clicked_label": "Masala > Dry Fruits",
        "name": "Almonds",
        "brand": "Zepto Select",
        "base_product_id": "123-abc",
        "group_id": "grp-123",
        "merchant_type": "zepto_store",
        "mrp": 500.0,
        "price": 450.0,
        "weight": "500 g",
        "shelf_life_in_hours": 720,
        "eta": "10 mins",
        "availability": "In Stock",
        "inventory": 50,
        "store_id": "store-001",
        "image_url": "https://hw.example.com/img.jpg",
        "product_url": "https://zepto.com/pn/almonds",
        "scraped_at": "2024-01-18 10:00:00",
        "pincode_input": "560001"
    }
    
    filename = "zepto_output_fields_preview.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=dummy_item.keys())
        writer.writeheader()
        writer.writerow(dummy_item)
        
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_schema_csv()
