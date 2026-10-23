# CreditFlow Intelligence

Credit decisioning → portfolio risk → BNPL checkout, built on public data.

**Status:** 🚧 Early development (Oct 2026) — loan mathematics module and unit tests in place.

## Project structure

```
creditflow-intelligence/
├── src/          # Python modules (e.g. loan_math.py: annuity instalments, amortisation schedules)
├── tests/        # Unit tests (pytest)
├── notebooks/    # Exploratory analysis
├── reports/      # Model cards, memos and write-ups
└── data/         # Local data only — not tracked by Git (see "Data" below)
```

## Setup

### Prerequisites
- [Python 3.14](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

### Installation

**1. Clone the repository**

Download the code from GitHub and move into the project folder.
```powershell
git clone https://github.com/ibrahim-ichsan/creditflow-intelligence.git
cd creditflow-intelligence
```

**2. Create a virtual environment**

A virtual environment keeps this project's libraries isolated from other Python projects on your machine, so versions never conflict.
```powershell
py -3.14 -m venv .venv
```

**3. Activate it**

When activation succeeds, your terminal prompt starts with `(.venv)`.
```powershell
.venv\Scripts\activate
```
If PowerShell blocks the script ("running scripts is disabled on this system"), run this once and then activate again:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**4. Install dependencies**

`requirements.txt` pins the exact library versions used in development, so your environment matches mine.
```powershell
pip install -r requirements.txt
```

> **macOS / Linux:** use `python3.14 -m venv .venv` for step 2 and `source .venv/bin/activate` for step 3. The other commands are the same.

### Run tests
```powershell
python -m pytest -v
```
All tests should pass.

### Data

This project uses the [Home Credit Default Risk](https://www.kaggle.com/competitions/home-credit-default-risk/data) dataset from Kaggle.

1. Sign in to Kaggle, open the competition page and accept the competition rules (required before downloading).
2. Download the data and extract the CSV files into `data/raw/`.

The data is **not included in this repository** because:
- the competition rules restrict redistribution of the dataset, and
- several files exceed GitHub's 100 MB file-size limit.

The `data/` folder is listed in `.gitignore`, so nothing in it is ever committed.