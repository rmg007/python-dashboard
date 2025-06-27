# Developer Onboarding Guide

Welcome to the Permit Dashboard project! This guide will help you get started, understand the codebase, and contribute effectively.

## Overview
Permit Dashboard is a data visualization tool for tracking permit data. It uses Dash, Plotly, Flask, and SQLite, with Google OAuth for authentication. The app loads permit data via ETL scripts and presents interactive charts and tables for analysis.

## Common Tasks
- **Add a chart/filter:** Edit or add a component in `components/`, then register callbacks in `callbacks/`.
- **Login/session logic:** Managed in `auth/` and `app.py`.
- **Debugging tips:**
  - Check logs in `app.log`
  - Inspect the SQLite DB at `data/dashboard.sqlite`
  - ETL scripts in `etl/` refresh data
  - Layout and callbacks are in `layout/` and `callbacks/`

## Sample .env
```
FLASK_SECRET_KEY=your-secret-key
OAUTH_GOOGLE_CLIENT_ID=
OAUTH_GOOGLE_CLIENT_SECRET=
ENABLE_SCHEDULED_JOBS=True
DEBUG=True
DATABASE_PATH=data/dashboard.sqlite
```

## Folder Map
- `etl/`: Data ingestion and refresh logic
- `components/`: Dash/Plotly UI components
- `callbacks/`: App interactivity
- `db/`: Database queries and helpers
- `auth/`: Authentication logic
- `tests/`: Unit and integration tests

## Internal Ownership
- General questions: #dev-permit-dashboard
- DB/ETL: Data team
- OAuth/Auth: Security team
- UI/UX: Frontend team

For more, see the README.md and CONTRIBUTING.md.
