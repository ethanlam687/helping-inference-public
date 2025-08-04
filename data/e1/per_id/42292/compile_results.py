import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from optimizer import optimize
import numpy as np
import pandas as pd
from ast import literal_eval
from utils import general
from agents import architect, generic_agent
from scipy.optimize import fmin

def fit_and_record(func, x0, args):
    """Runs fmin on `func`, returns (xopt, fopt)."""
    xopt, fopt, *_ = fmin(func, x0, args=args, full_output=True, disp=False)
    return np.atleast_1d(xopt), fopt

def main():
    # 1) Load the master move‐log
    df = pd.read_csv(
        "final_move_df.csv",
        converters={"config": literal_eval, "moveIDs": literal_eval}
    )

    records = []
    # 2) Loop ID × goal_type
    for ID, grp in df.groupby("ID"):
        for goal_type, sub in grp.groupby("goal_type"):
            config = sub.iloc[0]["config"]

            # — Literal architect —
            xopt, nll = fit_and_record(
                optimize.optimize.compute_ll_literal_architect,
                x0=[np.random.rand()],
                args=(config, sub)
            )
            records.append({
                "ID": ID,
                "goal_type": goal_type,
                "model": "literal",
                "param1": xopt[0],
                "param2": np.nan,
                "NLL": nll
            })

            # — Pragmatic architect —
            xopt, nll = fit_and_record(
                optimize.optimize.compute_ll_pragmatic_architect,
                x0=[np.random.rand(), np.random.rand()],
                args=(config, sub)
            )
            records.append({
                "ID": ID,
                "goal_type": goal_type,
                "model": "pragmatic",
                "param1": xopt[0],
                "param2": xopt[1],
                "NLL": nll
            })

            # — Salience + Pragmatic architect —
            xopt, nll = fit_and_record(
                optimize.optimize.compute_ll_sal_prag_architect,
                x0=[np.random.rand(), np.random.rand()],
                args=(config, sub)
            )
            records.append({
                "ID": ID,
                "goal_type": goal_type,
                "model": "sal_prag",
                "param1": xopt[0],
                "param2": xopt[1],
                "NLL": nll
            })

    # 3) Build DataFrame and save
    out = pd.DataFrame(records)
    out.to_csv("model_comparison_results.csv", index=False)
    print(f"✅ Wrote {len(out)} rows to model_comparison_results.csv")

if __name__ == "__main__":
    main()
