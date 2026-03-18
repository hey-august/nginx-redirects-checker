# Redirect Checker

Visual review tool for nginx redirect maps. Shows side-by-side iframe previews of the old (from) and new (to) URLs so you can approve, flag, or annotate each redirect.

## Setup

Grab the redirect map from the [`Devon/new-redirects`](https://github.com/signalwire/docs/blob/Devon/new-redirects/website/provisioning/nginx/redirects.map) branch of `signalwire/docs` and place it in this directory:

```bash
curl -fLo redirects.map "https://raw.githubusercontent.com/signalwire/docs/Devon/new-redirects/website/provisioning/nginx/redirects.map"
```

Then:

```bash
cd tools/redirect-checker
python3 server.py
# Open http://localhost:3000
```

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `A` | Approve |
| `F` | Flag |
| `R` | Reset to pending |
| `J` / `↓` | Next |
| `K` / `↑` | Previous |
| `N` | Focus notes |
| `/` | Focus search |

## Persistence

Review state auto-saves to both `localStorage` and `review-state.csv` on disk. Timestamped snapshots are kept in `history/` every 10 status changes (max 200). On reload, the CSV is loaded first, falling back to localStorage, then a fresh parse of `redirects.map`.

## Export

- **Export flagged** — CSV of flagged redirects with notes
- **Export all** — full CSV snapshot
- **Save** — download session as JSON
- **Import** — restore from a previously saved JSON session
