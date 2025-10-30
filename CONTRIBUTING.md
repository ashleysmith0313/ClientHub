# Contributing (How to update the hub)

## Editing data directly
1. Open the `data/` folder.
2. Edit `accounts.csv`, `pocs.csv`, or `requirements.csv` in the web editor.
3. Click **Commit changes**.

## Via Pull Request (recommended)
1. Create a new branch: `feature/add-acme`.
2. Edit CSVs and add any documents to `docs/`.
3. Commit and open a Pull Request.
4. The **Validate Data** workflow will run automatically. Fix any errors.
5. Merge the PR when checks pass.

## Data rules
- `account_id` must be unique and consistent across all three CSVs.
- `requirements.csv` values must be `0` or `1`.
- If you list a document in `accounts.csv`, the file must exist in `docs/`.
