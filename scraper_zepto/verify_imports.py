
try:
    from scrapers.zepto import ZeptoScraper
    import run_zepto_assortment_parallel
    import run_zepto_availability_parallel
    import dashboard.app_zepto
    print("Imports successful")
except Exception as e:
    print(f"Import failed: {e}")
