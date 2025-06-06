from optimizer import optimize
import pandas as pd
from ast import literal_eval


moveID_df = pd.read_csv("./data/e1/final_move_df.csv", converters = {"moveIDs": literal_eval, "config": literal_eval})

ID = 43580
ID_df = moveID_df[moveID_df["ID"] == ID]
currentConfig = list(ID_df["config"])[0]
beta = [0, 1, 2]


literal_NLL, prag_NLL = optimize.compute_firstmove_LL(beta, currentConfig, ID_df)

print("Literal NLL:", literal_NLL)
print("Pragmatic NLL:", prag_NLL)