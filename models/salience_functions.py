import pandas as pd, numpy as np, ast
from pathlib import Path

def row_col(idx, n_cols=18):
    return idx // n_cols, idx % n_cols

def compute_salience(move, center=44, n_cols=18):
    i = int(move.strip("()").split(",")[0])
    r0, c0 = row_col(i, n_cols)
    rc, cc = row_col(center, n_cols)
    return abs(r0-rc)+abs(c0-cc), np.hypot(r0-rc, c0-cc)

def sample_saliences(moves, n=1000, by_util=None, center=44, n_cols=18):
    """If by_util dict is passed, splits into serving vs non‑serving."""
    if by_util:
        groups = {
            k: [m for m in moves if (by_util[m]==k)]
            for k in (1, 0)  # 1=serving, 0=non‑serving
        }
        return {
            name: sample_saliences(grp, n, None, center, n_cols)
            for name, grp in (("serving", groups[1]), ("nonserv", groups[0]))
        }
    idxs = np.random.choice(moves, n, True)
    s = [compute_salience(m, center, n_cols)[0] for m in idxs]
    e = [compute_salience(m, center, n_cols)[1] for m in idxs]
    return {"step": np.mean(s), "euc": np.mean(e)}

def main():
    exp1 = pd.read_csv("data/e1/final_first_moves.csv")
    exp2 = pd.read_csv("data/e2/first_moves.csv")

    df = pd.concat(
    [exp1.assign(expt="E1"), exp2.assign(expt="E2")],
    ignore_index=True
)

    print(df.columns.tolist())

    
    # parse
    df["moves"] = df["first_move_possible_moves"].apply(ast.literal_eval)
    df["utils"] = df["utilities"].apply(ast.literal_eval)
    
    # compute all saliences in one go
    sal = df["first_move"].map(compute_salience)
    df[["step_obs","euc_obs"]] = pd.DataFrame(sal.tolist(), index=df.index)
    
    # random baseline
    base_all = df["moves"].map(lambda m: sample_saliences(m))
    df[["step_exp","euc_exp"]] = pd.DataFrame(base_all.tolist(), index=df.index)
    
    # utility‐split baseline
    split = df.apply(lambda r: sample_saliences(r["moves"], by_util=r["utils"]), axis=1)
    df[["step_s","euc_s","step_ns","euc_ns"]] = pd.DataFrame(
        [{**v, **{f"{k}_{t}":u for (k,d) in v.items() for t,u in d.items()}} 
         for v in split.tolist()], index=df.index
    )
    
    # final
    cols = ["expt","first_move","step_obs","step_exp","step_s","step_ns",
            "euc_obs","euc_exp","euc_s","euc_ns"]
    print(df[cols].head())

if __name__=="__main__":
    print("Running salience_analysis")
    main()