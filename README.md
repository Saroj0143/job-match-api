# Job Match API

A small, rule-based, fully explainable job recommendation API built for the
Job Match. It scores jobs for a candidate on
**skills, experience, location, and salary**, with must-have skills acting as a
hard filter.

## Tech Stack

- Python 3.12+ / FastAPI / SQLAlchemy 2.0
- PostgreSQL via Docker (or SQLite for local dev)
- pytest for tests

## How to Run Locally

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate.bat
# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the API
uvicorn src.main:app --reload