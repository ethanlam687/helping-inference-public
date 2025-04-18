import pandas as pd
import numpy as np
import ast

print('hello!')
# helper functions

def row_col(index: int, n_cols: int = 18) -> tuple:
    row, col = index // n_cols, index % n_cols
    return row, col

def compute_salience(move_string: str, center_index: int = 44, n_cols: int = 18) -> dict:
    start_idx = int(move_string.strip("()").split(",")[0])
    r0, c0 = row_col(start_idx, n_cols)
    rc, cc = row_col(center_index, n_cols)
    stepwise  = abs(r0 - rc) + abs(c0 - cc)
    euclidean = np.hypot(r0 - rc, c0 - cc)
    return {'stepwise': stepwise, 'euclidean': euclidean}

def sample_random_salience(possible_moves: list, n_samples: int = 1000,
                           center_index: int = 44, n_cols: int = 18) -> dict:
    sampled = np.random.choice(possible_moves, size=n_samples, replace=True)
    steps = []; eus = []
    for mv in sampled:
        s = compute_salience(mv, center_index, n_cols)
        steps.append(s['stepwise']); eus.append(s['euclidean'])
    return {'expected_stepwise': np.mean(steps),
            'expected_euclidean': np.mean(eus)}

def sample_random_salience_by_utility(possible_moves: list, utilities: dict,
                                      n_samples: int = 1000, center_index: int = 44,
                                      n_cols: int = 18) -> dict:
    serving     = [mv for mv in possible_moves if utilities.get(mv) == 1]
    nonserving  = [mv for mv in possible_moves if utilities.get(mv) != 1]
    out = {}
    if serving:
        r = sample_random_salience(serving, n_samples, center_index, n_cols)
        out['serving_stepwise'], out['serving_euclidean'] = r['expected_stepwise'], r['expected_euclidean']
    else:
        out['serving_stepwise'], out['serving_euclidean'] = np.nan, np.nan
    if nonserving:
        r = sample_random_salience(nonserving, n_samples, center_index, n_cols)
        out['nonserv_stepwise'], out['nonserv_euclidean'] = r['expected_stepwise'], r['expected_euclidean']
    else:
        out['nonserv_stepwise'], out['nonserv_euclidean'] = np.nan, np.nan
    return out

from pathlib import Path



# files to load
exp1 = pd.read_csv("helping_inference/data/e1/final_first_moves.csv")
exp2 = pd.read_csv("helping_inference/data/e2/first_moves.csv")
exp1['experiment'] = 'exp1'
exp2['experiment'] = 'exp2'
df = pd.concat([exp1, exp2], ignore_index=True)

# Parse list/dict columns
df['possible_moves_list'] = df['possible_moves'].apply(ast.literal_eval)
df['utilities_map']     = df['utilities'].apply(ast.literal_eval)

# Observed salience
obs = df['first_move'].apply(compute_salience)
df['stepwise_salience']   = obs.apply(lambda x: x['stepwise'])
df['euclidean_salience'] = obs.apply(lambda x: x['euclidean'])

# Baseline over all moves
base_all = df['possible_moves_list'].apply(lambda pm: sample_random_salience(pm))
df['expected_stepwise']   = base_all.apply(lambda x: x['expected_stepwise'])
df['expected_euclidean'] = base_all.apply(lambda x: x['expected_euclidean'])

# Baseline split by utility
split = df.apply(lambda row: sample_random_salience_by_utility(
    row['possible_moves_list'], row['utilities_map']), axis=1)
df['serving_stepwise']   = split.apply(lambda x: x['serving_stepwise'])
df['serving_euclidean'] = split.apply(lambda x: x['serving_euclidean'])
df['nonserv_stepwise']   = split.apply(lambda x: x['nonserv_stepwise'])
df['nonserv_euclidean']  = split.apply(lambda x: x['nonserv_euclidean'])

# Select and display results
result = df[[
    'experiment', 'first_move',
    'stepwise_salience', 'expected_stepwise', 'serving_stepwise', 'nonserv_stepwise',
    'euclidean_salience','expected_euclidean','serving_euclidean','nonserv_euclidean'
]]
print(result.head())