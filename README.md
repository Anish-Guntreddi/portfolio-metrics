# Engineering Portfolio — Metrics Dashboard

An interactive Streamlit dashboard for a 10-project engineering portfolio: five full-stack
applications and five systems-programming projects in C/C++.

- **KPIs** — 10 projects, 700 automated tests
- **Charts** — test coverage (full-stack vs systems) and throughput (log scale)
- **Deep dive** — per project: live-UI screenshot, architecture, the standout, and the security focus
- **Compare** — pick projects side by side
- **Filter** — by domain

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py        # http://localhost:8501
```

or with uv:

```bash
uv venv --python 3.12 && uv pip install -r requirements.txt
uv run streamlit run streamlit_app.py
```

## Deploy (free)

Hosted on **Streamlit Community Cloud**:

1. <https://share.streamlit.io> → **New app** → sign in with GitHub.
2. Repo: this one · Branch: `main` · **Main file:** `streamlit_app.py`.
3. Deploy → you get a public URL like `https://<app>.streamlit.app`.

Free-tier apps sleep when idle and wake on the next visit (~30s cold start).

## Editing

All project data lives in the `PROJECTS` list at the top of `streamlit_app.py`. Edit metrics,
descriptions, and architecture notes there; the charts and views update automatically.
