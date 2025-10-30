import os
import sys
import pandas as pd

DATA_DIR = "data"
DOCS_DIR = "docs"

errors = []

def err(msg):
    errors.append(msg)
    print(f"ERROR: {msg}")


def main():
    accounts = pd.read_csv(os.path.join(DATA_DIR, "accounts.csv"))
    pocs = pd.read_csv(os.path.join(DATA_DIR, "pocs.csv"))
    reqs = pd.read_csv(os.path.join(DATA_DIR, "requirements.csv"))

    # Required columns
    for fname, cols in [
        ("accounts.csv", {"account_id","name","industry","status","owner","priority","last_updated","documents","notes"}),
        ("pocs.csv", {"account_id","name","role","email","phone"}),
        ("requirements.csv", None), # dynamic columns allowed, but must include account_id
    ]:
        df = accounts if fname=="accounts.csv" else pocs if fname=="pocs.csv" else reqs
        if "account_id" not in df.columns:
            err(f"{fname} must include 'account_id' column")
        if cols:
            missing = cols - set(df.columns)
            if missing:
                err(f"{fname} missing columns: {sorted(list(missing))}")

    # account_id uniqueness
    if accounts["account_id"].duplicated().any():
        dups = accounts[accounts["account_id"].duplicated()]["account_id"].tolist()
        err(f"Duplicate account_id in accounts.csv: {dups}")

    # All pocs and reqs must map to existing account_id
    acct_ids = set(accounts["account_id"].astype(str))
    for df, name in [(pocs, "pocs.csv"), (reqs, "requirements.csv")]:
        bad = set(df["account_id"].astype(str)) - acct_ids
        if bad:
            err(f"{name} has unknown account_id(s): {sorted(list(bad))}")

    # requirements must be 0/1 only (excluding account_id)
    for c in [c for c in reqs.columns if c != "account_id"]:
        bad_vals = reqs[~reqs[c].isin([0,1])]
        if not bad_vals.empty:
            err(f"requirements.csv column '{c}' must contain only 0/1 values")

    # documents listed should exist in docs/
    for _, row in accounts.iterrows():
        docs = [x.strip() for x in str(row.get("documents","")) .split(',') if x.strip()]
        for d in docs:
            if not os.path.exists(os.path.join(DOCS_DIR, d)):
                err(f"Missing document file in docs/: {d} (referenced by account {row['account_id']})")

    if errors:
        print("\nValidation failed with errors above.")
        sys.exit(1)
    else:
        print("All data checks passed ✔")

if __name__ == "__main__":
    main()
