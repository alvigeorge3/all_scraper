from typing import TypedDict, Optional

class ProductItem(TypedDict):
    # Platform identification
    platform: str
    
    # Category information
    category: str
    subcategory: str
    clicked_label: str
    
    # Product information
    name: str
    brand: str
    base_product_id: Optional[str]
    product_id: Optional[str]
    group_id: Optional[str]
    merchant_type: Optional[str]
    
    # Pricing
    price: float
    mrp: float
    
    # Product details
    weight: str
    shelf_life_in_hours: Optional[str] # Changed to str to accommodate text
    shelf_life: Optional[str] # Explicit request from user
    
    # Seller/Manufacturer
    seller_details: Optional[str]
    manufacturer_details: Optional[str]
    marketer_details: Optional[str]
    merchant_id: Optional[str]
    
    # Availability
    availability: str
    inventory: Optional[int]
    variant_count: Optional[int]
    variant_in_stock_count: Optional[int]
    
    # Delivery
    eta: str
    store_id: Optional[str]
    
    # URLs
    image_url: str
    product_url: str
    
    # Metadata
    scraped_at: str
    pincode_input: str

class AvailabilityResult(TypedDict):
    input_pincode: str
    url: str
    platform: str
    name: str # Enriched from page if possible
    price: float
    mrp: float
    availability: str # "In Stock", "Out of Stock", "Unknown"
    
    # Detailed fields for Availability Scraping Mode
    seller_details: Optional[str]
    manufacturer_details: Optional[str]
    marketer_details: Optional[str]
    variant_count: Optional[int]
    variant_in_stock_count: Optional[int]
    inventory: Optional[int]
    
    scraped_at: str
    error: Optional[str]
