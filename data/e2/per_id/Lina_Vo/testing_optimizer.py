import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from optimizer import optimize
import numpy as np
import pandas as pd
from ast import literal_eval
from utils import general
from agents import architect, generic_agent

ID = os.path.basename(os.getcwd())

# imports
moveID_df = pd.read_csv("final_move_df.csv", converters={"moveIDs": literal_eval, "config": literal_eval})

print(f"🟢 Starting optimization for ID: {ID}")
print("Current working directory:", os.getcwd())
print("DataFrame shape:", moveID_df.shape)
print("Goal types:", moveID_df['goal_type'].unique())


results = []

for goal_type, subdf in moveID_df.groupby("goal_type"):
    print(f"\n🔍 Processing goal_type: {goal_type}")
    if subdf.empty:
        print(f"⚠️ Skipping {goal_type} — no data.")
        continue
    config = subdf["config"].iloc[0]

    # 1. sal_prag model
    try:
        print("Optimizing sal_prag model...")
        _, (alpha_opt, beta_opt) = optimize.optimize_sal_prag_architect(subdf)
        salprag_ll = optimize.compute_ll_sal_prag_architect([alpha_opt, beta_opt], config, subdf)
        results.append({
            "ID": ID,
            "goal_type": goal_type,
            "model": "sal_prag",
            "parameter1": alpha_opt,
            "parameter2": beta_opt,
            "NLL": salprag_ll
        })
        print(f"✅ sal_prag done: alpha={alpha_opt:.3f}, beta={beta_opt:.3f}, NLL={salprag_ll:.2f}")
    except Exception as e:
        print(f"❌ Error optimizing sal_prag for {goal_type}: {e}")
        continue

    # 2. literal model
    try:
        print("Optimizing literal model...")
        _, beta_literal = optimize.optimize_literal_architect(subdf)
        literal_nll = optimize.compute_ll_literal_architect(beta_literal, config, subdf)
        results.append({
            "ID": ID,
            "goal_type": goal_type,
            "model": "literal",
            "parameter1": beta_literal,
            "parameter2": None,
            "NLL": float(literal_nll)
        })
        print(f"✅ literal done: beta={beta_literal:.3f}, NLL={literal_nll:.2f}")
    except Exception as e:
        print(f"❌ Error optimizing literal for {goal_type}: {e}")
        continue

    # 3. pragmatic model
    try:
        print("Optimizing pragmatic model...")
        _, (goal_noise, action_noise) = optimize.optimize_pragmatic_architect(subdf)
        pragmatic_nll = optimize.compute_ll_pragmatic_architect([goal_noise, action_noise], config, subdf)
        results.append({
        "ID": ID,
        "goal_type": goal_type,
        "model": "pragmatic",
        "parameter1": goal_noise,
        "parameter2": action_noise,
        "NLL": float(pragmatic_nll)
    })
        print(f"✅ pragmatic done: goal_noise={goal_noise:.3f}, action_noise={action_noise:.3f}, NLL={pragmatic_nll:.2f}")
    except Exception as e:
        print(f"❌ Error optimizing pragmatic for {goal_type}: {e}")
        continue

results_df = pd.DataFrame(results)
results_df.to_csv("model_results.csv", index=False)

print("finished model fitting and optimization for ID:", ID)
print(results_df)