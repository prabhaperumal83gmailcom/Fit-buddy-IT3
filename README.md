# FitBuddy

Clean restart package for the FitBuddy AI Fitness Plan Generator. Uses FastAPI, Jinja2, SQLite/SQLAlchemy and the Gemini API. Includes 7-day plans, feedback revision, nutrition/recovery tips, persistence, user listing, tests and resilient Gemini retry/fallback handling.

## Windows PowerShell

```powershell
cd "C:\path\to\FitBuddy"
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/

For activation policy errors:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Run tests:
```powershell
pytest -q
```

Never commit `.env`. The project retries transient 429/5xx Gemini errors, tries configured fallback models, and uses a deterministic local fallback when Gemini remains unavailable.
