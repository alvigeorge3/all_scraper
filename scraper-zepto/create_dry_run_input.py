import pandas as pd

def create_input_file():
    data = {
        'Pincode': ['560001'],
        'Product_Url': ['https://www.zepto.com/cn/masala-dry-fruits-more/masala-dry-fruits-more/cid/0c2ccf87-e32c-4438-9560-8d9488fc73e0/scid/8b44cef2-1bab-407e-aadd-29254e6778fa']
    }
    df = pd.DataFrame(data)
    df.to_excel('zepto_assortment_input.xlsx', index=False)
    print("Created zepto_assortment_input.xlsx")

if __name__ == '__main__':
    create_input_file()
