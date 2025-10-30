# Strategic Accounts Hub (Streamlit + GitHub)

This is a simple, **GitHub-first Strategic Accounts hub** your team can open in a browser. It shows at-a-glance info for each account: requirements, points of contact (POCs), status, and related documents.

- **No database needed** — just CSV files in `data/` and documents in `docs/`.
- **Deployed on Streamlit Community Cloud** — free hosting connected to this GitHub repo.
- **Edits via GitHub** — propose changes in Pull Requests; a check validates the CSVs.

## Quick Start (10 minutes)

### A) Use this template
1. Click **Use this template** (or **Fork**) on GitHub to create your copy.
2. In your new repo, keep the structure as-is.

### B) Deploy to Streamlit Cloud
1. Go to **share.streamlit.io** and sign in with GitHub.
2. Click **New app** → select your repo and `streamlit_app.py` as the file → **Deploy**.
3. That’s it. The app reads your `data/` and shows your accounts.

> **Tip:** When you change CSVs or docs on GitHub, Streamlit will pick it up after the next app reload. If it doesn’t, click **Rerun** in the app.

## Editing data (layman’s terms)
- Go to `data/accounts.csv` to add or edit accounts.
- Go to `data/pocs.csv` to add or edit points of contact.
- Go to `data/requirements.csv` to add or edit each account’s requirement checkboxes.
- Upload PDFs/PowerPoints into `docs/` and reference them by filename in `accounts.csv` (comma-separated if multiple).

When you’re done editing, **Commit** changes (or open a **Pull Request**). The **Validate Data** GitHub Action will check for common mistakes (missing required columns, invalid account IDs, etc.).

## How the app is organized
- **Left sidebar:** quick filters (industry, status, owner) and a search box.
- **Main table:** list of all strategic accounts with a one-click **Open** link.
- **Account page:** full view with requirements status, POCs, and document links. You can also **download a Markdown brief** prefilled for that account.

## Limitations (by design)
- The app is **read-only** in production. To change data, edit CSVs on GitHub or open a Pull Request.
- Uploading files inside the app will **not** permanently save them. Instead, add files to `docs/` via GitHub.

## Local development
```bash
# 1) Clone your repo
git clone https://github.com/your-org/strategic-accounts-hub.git
cd strategic-accounts-hub

# 2) Create a virtual env (optional) and install deps
pip install -r requirements.txt

# 3) Run the app locally
streamlit run streamlit_app.py
```

## License
MIT — see `LICENSE`.
