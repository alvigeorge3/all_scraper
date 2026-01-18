import pandas as pd
import os

# Create a dataframe with test data from user request
data = {
    'Pincode': ['560001'],
    'Url': [
        'https://www.zepto.com/cn/fruits-vegetables/all/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/e78a8422-5f20-4e4b-9a9f-22a0e53962e3?srsltid=AfmBOooH2hwgeQIUmSg-u5sbweT5D7xAyuZ7vt02x1djSuxxTT9oHSwq'
    ]
}

df = pd.DataFrame(data)

output_file = 'zepto_assortment_input.xlsx'
df.to_excel(output_file, index=False)
print(f"Created {output_file} with user provided test data.")
