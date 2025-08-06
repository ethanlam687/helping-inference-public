import pandas as pd
import ast

# Load the CSV
df = pd.read_csv("data/e2/final.csv")

# Convert 'config' and 'moveIDs' from strings to actual Python objects
df['config'] = df['config'].apply(ast.literal_eval)
df['moveIDs'] = df['moveIDs'].apply(ast.literal_eval)

# Now they're proper Python lists/tuples
print(df.dtypes)
print(df.iloc[0]['config'])   # This should be a list, not a string
print(df.iloc[0]['moveIDs'])  # This should be a list of tuples


