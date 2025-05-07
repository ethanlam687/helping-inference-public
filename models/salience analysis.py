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

def random_baseline_salience(config, goal_type=None, n_samples=1000, n_cols=18):
    
    """
    Compute the baseline random saliences for a given board config by
       - sampling n_samples moves at random
       - computing their salience relative to the appropriate center
       - averaging the stepwise and euclidean salience scores
    
    Arguments:
        config: the current board configuration
        goal_type: one of "cover"/"uncover" or None; if None, uses TRUE_CENTER
        n_samples: number of random moves to sample (default=1000)
        n_cols: grid width (18)
    
    Returns:
        dict with keys
          'stepwise' --> average stepwise salience
          'euclidean' --> average Euclidean salience
    """

    # define which center to use
    center_idx = pick_center(goal_type) if goal_type is not None else TRUE_CENTER
    
    # enumerate all legal moves
    moveable = general.moveable_indices(config)
    drop_locs = general.possible_drop_locations(config)
    combs = [(m,d) for m in moveable for d in drop_locs if (m - d) != n_cols]
    
    if not combs:
        return {"stepwise": np.nan, "euclidean": np.nan}
    step_vals, euc_vals = [], []
    for _ in range(n_samples):
        m,d = random.choice(combs)
        sal = compute_salience(f"({m},{d})", center_idx, n_cols)
        step_vals.append(sal["stepwise_salience"])
        euc_vals.append(sal["euclidean_salience"])
    return {"stepwise": float(np.mean(step_vals)), "euclidean": float(np.mean(euc_vals))}

def add_baseline_columns(df: pd.DataFrame, n_samples=1000) -> pd.DataFrame:
    b = df.apply(
        lambda r: pd.Series(random_baseline_salience(r["config"], r["goal_type"], n_samples)),
        axis=1
    ).rename(columns={"stepwise":"random_stepwise_salience", "euclidean":"random_euclidean_salience"})
    return pd.concat([df, b], axis=1)

def main():
    files = [
        ("data/e1/final_first_moves.csv", None, "E1"),
        ("data/e2/first_moves.csv", "data/e2/final_move_df.csv", "E2")
    ]
    all_dfs = []
    for moves_path, config_path, label in files:
        df_moves = pd.read_csv(moves_path)
        # for E1, keep only architects
        if label == "E1" and "role" in df_moves.columns:
            df_moves = df_moves[df_moves['role'] == "architect"]

        df_moves['experiment'] = label
        df_moves['goal_type'] = df_moves['goal'].str.split().str[0]

        if config_path:
            # E2 branch: load & parse configs
            df_config = pd.read_csv(config_path)
            df_config['config'] = df_config['config'].apply(ast.literal_eval)

            # merge on anonID so each row has its starting board
            df = df_moves.merge(
                df_config[['importId','config']],
                on='importId',
                how='left'
            )
            # observed salience
            df = add_salience_columns(df)
            # random-baseline salience
            df = add_baseline_columns(df, n_samples=1000)

        else:
            # E1 branch: observed only
            df = add_salience_columns(df_moves)
            # pad the baseline columns with NaN for consistency
            df['random_stepwise_salience'] = np.nan
            df['random_euclidean_salience'] = np.nan

        all_dfs.append(df)

    combined = pd.concat(all_dfs, ignore_index=True)
    combined.to_csv("./analysis/salience_first_moves.csv", index=False)

    summary = (
        combined.groupby(['goal_type', 'experiment'])[['stepwise_salience', 'euclidean_salience', 'random_stepwise_salience', 'random_euclidean_salience']]
        .agg(['mean', 'std', 'count'])
    )
    print(summary)


if __name__ == "__main__":
    main()
