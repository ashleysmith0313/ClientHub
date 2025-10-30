import os
import io
import pandas as pd
import streamlit as st
from slugify import slugify

APP_TITLE = "Strategic Accounts Hub"
DATA_DIR = "data"
DOCS_DIR = "docs"

@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Trim whitespace from string columns
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].fillna("").astype(str).str.strip()
    return df

@st.cache_data
def load_data():
    accounts = load_csv(os.path.join(DATA_DIR, "accounts.csv"))
    pocs = load_csv(os.path.join(DATA_DIR, "pocs.csv"))
    reqs = load_csv(os.path.join(DATA_DIR, "requirements.csv"))

    # Enforce types
    accounts["account_id"] = accounts["account_id"].astype(str)
    pocs["account_id"] = pocs["account_id"].astype(str)
    reqs["account_id"] = reqs["account_id"].astype(str)

    return accounts, pocs, reqs


def quick_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")
    search = st.sidebar.text_input("Search (name, notes)")

    industries = sorted([x for x in df["industry"].unique() if x])
    statuses = sorted([x for x in df["status"].unique() if x])
    owners = sorted([x for x in df["owner"].unique() if x])

    col1, col2, col3 = st.sidebar.columns(3)
    sel_industry = col1.multiselect("Industry", industries)
    sel_status = col2.multiselect("Status", statuses)
    sel_owner = col3.multiselect("Owner", owners)

    out = df.copy()
    if search:
        s = search.lower()
        out = out[out["name"].str.lower().str.contains(s) | out["notes"].str.lower().str.contains(s)]
    if sel_industry:
        out = out[out["industry"].isin(sel_industry)]
    if sel_status:
        out = out[out["status"].isin(sel_status)]
    if sel_owner:
        out = out[out["owner"].isin(sel_owner)]

    return out


def account_row_link(row):
    # Use query params so links work in Streamlit Cloud
    acct = row["account_id"]
    label = "Open"
    return f"[ {label} ](?account={acct})"


def render_table(accounts: pd.DataFrame):
    if accounts.empty:
        st.info("No accounts match your filters.")
        return

    table = accounts[[
        "account_id", "name", "industry", "status", "owner", "priority", "last_updated"
    ]].copy()

    table["Open"] = accounts.apply(account_row_link, axis=1)
    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "account_id": st.column_config.TextColumn("ID", width="small"),
            "name": st.column_config.TextColumn("Account"),
            "industry": st.column_config.TextColumn("Industry"),
            "status": st.column_config.TextColumn("Status"),
            "owner": st.column_config.TextColumn("Owner"),
            "priority": st.column_config.NumberColumn("Priority"),
            "last_updated": st.column_config.TextColumn("Last Updated"),
            "Open": st.column_config.LinkColumn(" ")
        }
    )


def req_badge(ok: bool) -> str:
    return "✅" if ok else "⭕"


def docs_list(doc_string: str):
    if not doc_string:
        st.write("—")
        return
    files = [x.strip() for x in doc_string.split(",") if x.strip()]
    for f in files:
        path = os.path.join(DOCS_DIR, f)
        if os.path.exists(path):
            st.markdown(f"- [{f}]({path})")
        else:
            st.markdown(f"- {f} (missing in `docs/`) ")


def account_page(account_id: str, accounts: pd.DataFrame, pocs: pd.DataFrame, reqs: pd.DataFrame):
    row = accounts[accounts["account_id"] == account_id]
    if row.empty:
        st.error("Account not found.")
        return
    row = row.iloc[0]

    st.page_link("?", label="← Back to all accounts")
    st.title(row["name"]) 
    st.caption(f"ID: {row['account_id']} • Industry: {row['industry']} • Status: {row['status']} • Owner: {row['owner']} • Priority: {row['priority']}")

    c1, c2 = st.columns([2,1])
    with c1:
        st.subheader("Requirements")
        r = reqs[reqs["account_id"] == account_id]
        if r.empty:
            st.info("No requirements recorded yet.")
        else:
            r = r.iloc[0]
            checklist_cols = [c for c in r.index if c not in ("account_id",)]
            for c in checklist_cols:
                # tolerate non-binary by bool casting of truthy values
                try:
                    val = bool(int(r[c]))
                except Exception:
                    val = str(r[c]).strip() in ("1","true","True","yes","Yes","y")
                st.write(f"{req_badge(val)} {c}")

        st.subheader("Documents")
        docs_list(row.get("documents", ""))

    with c2:
        st.subheader("Points of Contact")
        p = pocs[pocs["account_id"] == account_id]
        if p.empty:
            st.info("No POCs added yet.")
        else:
            st.dataframe(p[["name","role","email","phone"]], hide_index=True, use_container_width=True)

    st.divider()

    st.subheader("Download Account Brief (Markdown)")
    brief = build_account_brief(row, pocs[pocs["account_id"] == account_id], reqs[reqs["account_id"] == account_id])
    st.download_button(
        label="Download ACCOUNT_BRIEF.md",
        file_name=f"{slugify(row['name'])}-brief.md",
        mime="text/markdown",
        data=brief.encode("utf-8")
    )


def build_account_brief(account_row: pd.Series, pocs_df: pd.DataFrame, reqs_df: pd.DataFrame) -> str:
    lines = []
    lines.append(f"# {account_row['name']}")
    lines.append("")
    lines.append(f"**ID:** {account_row['account_id']}  ")
    lines.append(f"**Industry:** {account_row['industry']}  ")
    lines.append(f"**Status:** {account_row['status']}  ")
    lines.append(f"**Owner:** {account_row['owner']}  ")
    lines.append(f"**Priority:** {account_row['priority']}  ")
    lines.append(f"**Last Updated:** {account_row['last_updated']}  ")
    lines.append("")
    lines.append("## Requirements")
    if not reqs_df.empty:
        r = reqs_df.iloc[0]
        checklist_cols = [c for c in r.index if c != "account_id"]
        for c in checklist_cols:
            try:
                checked = 'x' if bool(int(r[c])) else ' '
            except Exception:
                checked = 'x' if str(r[c]).strip() in ('1','true','True','yes','Yes','y') else ' '
            lines.append(f"- [{checked}] {c}")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Points of Contact")
    if pocs_df.empty:
        lines.append("- (none)")
    else:
        for _, p in pocs_df.iterrows():
            lines.append(f"- **{p['name']}** — {p['role']} — {p['email']} — {p['phone']}")
    lines.append("")
    lines.append("## Documents")
    docs = [x.strip() for x in (account_row.get('documents','') or '').split(',') if x.strip()]
    for d in docs:
        lines.append(f"- {d}")
    if not docs:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Notes")
    lines.append(account_row.get('notes',''))
    return "\n".join(lines)


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption("Single source of truth for Strategic Accounts — powered by CSVs in GitHub.")

    accounts, pocs, reqs = load_data()

    # Route based on query param
    params = st.query_params
    account_id = params.get("account", [None])
    if isinstance(account_id, list):
        account_id = account_id[0] if account_id else None

    if account_id:
        account_page(account_id, accounts, pocs, reqs)
        return

    # Home / Table view
    st.subheader("All Strategic Accounts")
    filtered = quick_filters(accounts)
    render_table(filtered)

    st.info(
        "To update data, edit CSVs in `data/` and files in `docs/` on GitHub. "
        "Changes are reflected on the next app reload."
    )


if __name__ == "__main__":
    main()
