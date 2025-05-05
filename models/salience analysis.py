import re, ast
import random
import numpy as np
import pandas as pd
import warnings

if not hasattr(np, "VisibleDeprecationWarning"):
    np.VisibleDeprecationWarning = DeprecationWarning
from utils import general

# Salience constants
TRUE_CENTER = 44
GOAL_CENTER = 73 

# salience helper functions

def pick_center(goal_type: str) -> int:
    return GOAL_CENTER if goal_type in ("cover", "uncover") else TRUE_CENTER

def row_col(index: int, n_cols: int = 18) -> tuple[int,int]:
    # Convert a flat grid index into (row, col) on an n_cols-wide grid.
    return index // n_cols, index % n_cols



# salience computation functions

def compute_salience(move_str: str,
                     center_idx: int,
                     n_cols: int = 18) -> dict[str,float]:
    """
    Compute Stepwise and Euclidean salience from chosen center
    """
    idx = int(move_str.strip("()").split(",")[0])
    r, c = row_col(idx, n_cols)
    rc, cc = row_col(center_idx, n_cols)
    return {
        "stepwise_salience": abs(r - rc) + abs(c - cc),
        "euclidean_salience": np.hypot(r - rc, c - cc)
    }


def add_salience_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a df with a column of move-strings, compute and append
    'stepwise_salience' and 'euclidean_salience' columns.
    """
    sal = df.apply(
        lambda r: compute_salience(
            r['first_move'],
            center_idx=pick_center(r['goal_type'])
        ),
        axis=1
    )
    sal_df = pd.DataFrame(sal.tolist(), index=df.index)
    return pd.concat([df, sal_df], axis=1)

""""
# WORING ON DEBUG

def random_salience_baseline(row, n_samples: int = 1000):
    # parse configuration
    config = parse_config(row["before_first_move"])
    # find all legal moves
    movs  = general.moveable_indices(config)
    drops = general.possible_drop_locations(config)
    all_moves = [(m,d) for m in movs for d in drops if m-d != 18]

    # if there are no legal moves, return NaNs for everything
    if not all_moves:
        return pd.Series({
            "avg_rand_step":   np.nan,
            "avg_rand_euc":    np.nan,
            "diff_rand_step":  np.nan,
            "diff_rand_euc":   np.nan,
            "avg_serv_step":   np.nan,
            "avg_serv_euc":    np.nan,
            "diff_serv_step":  np.nan,
            "diff_serv_euc":   np.nan,
        })

    # actual move salience
    actual = compute_salience(row["first_move"])

    # uniform-random baseline (safe now since all_moves non-empty)
    samp = random.choices(all_moves, k=n_samples)
    movs = general.moveable_indices(config)
    drops = general.possible_drop_locations(config)
    all_moves = [(m, d) for m in movs for d in drops if m - d != 18]

    # uniform‐random baseline
    samp = random.choices(all_moves, k=n_samples)
    rand_steps = [ compute_salience(f"({m},{d})")["stepwise_salience"] for m,d in samp ]
    rand_eucs = [ compute_salience(f"({m},{d})")["euclidean_salience"] for m,d in samp ]
    avg_rand_s = np.mean(rand_steps)
    avg_rand_e = np.mean(rand_eucs)

    # goal‐serving moves only (utility == 1)
    serve = [mv for mv in all_moves
             if general.compute_move_utility(config, mv, row["goal"]) == 1]
    if serve:
        samp2 = random.choices(serve, k=n_samples)
        serv_steps = [ compute_salience(f"({m},{d})")["stepwise_salience"] for m,d in samp2 ]
        serv_eucs = [ compute_salience(f"({m},{d})")["euclidean_salience"] for m,d in samp2 ]
        avg_serv_s = np.mean(serv_steps)
        avg_serv_e = np.mean(serv_eucs)
    else:
        avg_serv_s = avg_serv_e = np.nan

    return pd.Series({
        "avg_rand_step": avg_rand_s,
        "avg_rand_euc": avg_rand_e,
        "diff_rand_step": actual["stepwise_salience"] - avg_rand_s,
        "diff_rand_euc": actual["euclidean_salience"] - avg_rand_e,
        "avg_serv_step": avg_serv_s,
        "avg_serv_euc": avg_serv_e,
        "diff_serv_step": actual["stepwise_salience"] - avg_serv_s,
        "diff_serv_euc": actual["euclidean_salience"] - avg_serv_e,
    })
"""

def main():
    files = [
        ("data/e1/final_first_moves.csv", "E1"),
        ("data/e2/first_moves.csv", "E2")
    ]
    dfs = []
    for path, label in files:
        df = pd.read_csv(path)
        # only E2 has a 'role' column to filter
        if label == "E2" and "role" in df.columns:
            df = df[df['role'] == 'architect']
        df['experiment'] = label
        df['goal_type']  = df['goal'].str.split().str[0]
        df = add_salience_columns(df)
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)

    summary = (
        combined
        .groupby(['goal_type', 'experiment'])[['stepwise_salience', 'euclidean_salience']]
        .agg(['mean', 'std', 'count'])
    )
    print(summary)

if __name__ == "__main__":
    main()
