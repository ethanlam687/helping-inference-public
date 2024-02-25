import pandas as pd
# Set display options to show all columns and rows
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

filepathe1 = '../data/e1/excluded_final_moves_df.csv'
filepathe2 = '../data/e2/final_e2_participants.csv'

dfe1 = pd.read_csv(filepathe1)
dfe2 = pd.read_csv(filepathe2)

e1_unique_ids_count = dfe1['ID'].nunique()
e1_ids = set(dfe1['ID'].value_counts().index.tolist())
e2_unique_importID_count = dfe2['importId'].nunique()
importIds_e2_distribution = dfe2['importId'].value_counts()
importIds_e2_distribution = set(importIds_e2_distribution[importIds_e2_distribution > 1].index)


less_used_importIds = e1_ids.difference(importIds_e2_distribution)
col = ['importId']
pd = pd.DataFrame(list(less_used_importIds), columns=col)
pd.to_csv('../data/e2/less_used_importIDs.csv', index=False)
