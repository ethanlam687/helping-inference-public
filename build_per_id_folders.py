#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
import shutil

# ─── CONFIG ────────────────────────────────────────────────────────────────
# Assumes you run this from the helping-inference/ directory
data_e1         = Path("data") / "e1"
per_id_root     = data_e1 / "per_id"
template_id     = "42292"  # ID folder to copy templates from (you must have this already)
template_folder = per_id_root / template_id               # your existing template folder
master_csv      = data_e1 / "final_move_df.csv"       # full master CSV
# ──────────────────────────────────────────────────────────────────────────

# 1. Read the full final_move_df.csv
df = pd.read_csv(master_csv)

# 2. Find all .py and .sh in data/e1/per_id/42292
template_files = [
    f for f in template_folder.iterdir()
    if f.is_file() and f.suffix in {".py", ".sh"}
]

# 3. Build one folder per unique ID
for pid in df["ID"].unique():
    pid_str = str(pid)
    dst = per_id_root / pid_str
    dst.mkdir(parents=True, exist_ok=True)

    # 3a. Copy template scripts into data/e1/per_id/<pid>/
    if pid_str != template_id:
        for src in template_files:
            shutil.copy2(src, dst / src.name)

    # always write the filtered CSV
    df[df["ID"] == pid].to_csv(dst / "final_move_df.csv", index=False)

print("✅ Finished building per-ID folders under data/e1/per_id/") 
