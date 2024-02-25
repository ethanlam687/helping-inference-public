import pandas as pd
# Set display options to show all columns and rows
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


filepathe1 = 'data/e1/final_move_df.csv'
filepathe2 = 'data/e2/cleaned_e2.csv'
dfe1 = pd.read_csv(filepathe1)
dfe2 = pd.read_csv(filepathe2)

e1_unique_ids_count = dfe1['ID'].nunique()
# print(e1_unique_ids_count) # e1 returns 89 unique IDs(in e2 called importId)

e2_unique_ids_count = dfe2['ID'].nunique()
# print(e2_unique_ids_count) # 136 unique IDs for e2(meaning people who played e2)
e2_unique_importID_count = dfe2['importId'].nunique()
# print(e2_unique_importID_count) # 61 unique ImportIDs for e2

importIds_e2_distribution = dfe2['importId'].value_counts()
# an importId is used 10 times per ID, anything great than 10 is used more than twice
importIds_e2_distribution = importIds_e2_distribution[importIds_e2_distribution > 10]
print(len(importIds_e2_distribution)) 
"""
32 ImportIDs used twice, 26 used 3 times: Total 58 ImportIDs used more than twice
Meaning 3 ImportIDs are used only once. There other 31 are never used. 
"""