import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


filepath = 'data/e2/sona_combined.xlsx'
filepath_to_read = 'data/e2/sona_20231218_gameData.xlsx'

filepath_to_write = 'data/e2/sona_20231218_gameData_cleaned.xlsx'


df_combinded = pd.read_excel(filepath, sheet_name='sona_combined')
first_try_gameIds = df_combinded['Attempt 1'] 
# print(first_try_gameIds.nunique()) # 75 unique first trys

df_raw = pd.read_excel(filepath_to_read, sheet_name='gameData')
# only get rows which have gameID from first game of participants
filtered_df = df_raw[df_raw['gameId'].isin(first_try_gameIds)]

f = open(filepath_to_write, 'x')

filtered_df.to_excel(filepath_to_write, index=False)




