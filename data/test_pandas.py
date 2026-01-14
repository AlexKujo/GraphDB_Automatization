import pandas as pd

df = pd.read_excel(r'data\test_table.xlsx')

# print(df.columns.tolist())

print(df['Date'])
