import re, ast
import random
import numpy as np
import pandas as pd
import warnings

if not hasattr(np, "VisibleDeprecationWarning"):
    np.VisibleDeprecationWarning = DeprecationWarning
from utils import general

def parse_config(raw):
    """
    Given the raw CSV cell, extract a list of color strings.
    Handles:
      - Python list literal: "['white','red',...]"
      - NumPy array string: "array(['white',...], dtype=object)"
      - Any other wrapper, by finding all quoted tokens.
    """
    if isinstance(raw, str):
        # Find all occurrences of 'white', 'red', 'blue', or 'green'.
        colors = re.findall(r"'([^']+)'", raw)
        return colors
    else:
        # Already a list
        return raw

def row_col(index: int, n_cols: int = 18) -> tuple[int,int]:
    # Convert a flat grid index into (row, col) on an n_cols-wide grid.
    return index // n_cols, index % n_cols

def compute_salience(move_str: str,
                     center_idx: int = 44,
                     n_cols: int = 18) -> dict[str,float]:
    """
    Compute Manhattan ("stepwise") and Euclidean ("euclidean") distance
    from the grid center for a single move.

    - move_str: players' first move; something like "(23,5)" and pull out the first number as the flat index
    - center_idx: flat index of the grid center
    - n_cols: number of columns in the grid

    Returns {"stepwise": ..., "euclidean": ...}.
    """
    idx = int(move_str.strip("()").split(",")[0])
    r, c = row_col(idx, n_cols)
    rc, cc = row_col(center_idx, n_cols)
    return {
        "stepwise_salience": abs(r - rc) + abs(c - cc),
        "euclidean_salience": np.hypot(r - rc, c - cc)
    }

def add_salience_columns(df: pd.DataFrame,
                         move_col: str = "first_move",
                         center_idx: int = 44,
                         n_cols: int = 18) -> pd.DataFrame:
    """
    Given a DataFrame with a column of move-strings, compute and append
    'stepwise_salience' and 'euclidean_salience' columns.
    """
    sal = df[move_col].apply(compute_salience,
                             center_idx = center_idx,
                             n_cols = n_cols)
    sal_df = pd.DataFrame(sal.tolist(), index=df.index)
    return pd.concat([df, sal_df], axis = 1)
        
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

def load_and_process_csv(path: str, label: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "role" in df.columns:
        df = df[df["role"] == "architect"]
    df = add_salience_columns(df)
    return df.assign(experiment=label)

def main():
    files = [
        ("data/e1/final_first_moves.csv", "E1"),
        ("data/e2/first_moves.csv", "E2")
    ]
    combined = pd.concat(
        (load_and_process_csv(path, label) for path, label in files),
        ignore_index=True
    )
    combined["goal_type"] = combined["goal"].str.split().str[0]

    baseline = combined.apply(random_salience_baseline, axis = 1)
    combined = pd.concat([combined, baseline], axis = 1)

    metrics = [
        "stepwise_salience", "euclidean_salience",           # observed saliences
      "avg_rand_step", "avg_rand_euc",   # randomly sampled saliences
      "avg_serv_step","avg_serv_euc"     # goal serving random only
    ]

    summary = (
        combined.groupby(["goal_type", "experiment"])[metrics]
        .agg(["mean", "std", "count"])
    )
    print(summary)

    combined.to_csv("salience_with_baselines.csv", index=False)
    print("\n→ Wrote salience_with_baselines.csv")

if __name__ == "__main__":
    main()
