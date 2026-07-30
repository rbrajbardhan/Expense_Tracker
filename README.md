# Expense Tracker

Expense Tracker is a Django 5 personal finance application for logging income and expenses, managing budgets and savings goals, reviewing analytics, and exporting transaction reports. It uses a custom user model with per-user currency and savings target settings, plus a profile model for optional occupation, phone number, and profile picture metadata.

## What the app does

The project is split into three Django apps:

- `accounts` handles sign up, login, logout, profile editing, and password changes.
- `tracker` manages the core finance workflow: global and user-defined categories, income, expenses, budgets, and savings goals.
- `analytics` provides a dashboard view, chart data API, AI insights, and CSV or Excel report export.

Implemented behavior includes:

- custom user accounts with currency selection and monthly savings target fields
- automatic `UserProfile` creation through model signals
- CRUD screens for categories, incomes, expenses, budgets, and savings goals
- budget progress tracking with warning messages when spending reaches 75%, 90%, or exceeds 100%
- savings goal contributions and completion tracking
- analytics charts for 6-month income vs. expense trends, current-month expense category distribution, and budget versus actual spending
- AI insights based on historical expenses, including linear regression forecasts, anomaly detection, spending-velocity risk checks, and savings recommendations
- transaction report pages with CSV and Excel export

## Tech Stack

- Django 5.2
- SQLite
- Django templates
- Bootstrap 5 and Bootstrap Icons loaded from CDNs
- Chart.js for charts
- Pandas, NumPy, scikit-learn, and python-dateutil for analytics
- openpyxl for Excel export
- Pillow for profile image uploads

## Project Layout

```text
expense_tracker/
├── accounts/        # Authentication, custom user model, profile management
├── analytics/       # Charts, AI insights, report export
├── tracker/         # Categories, income, expenses, budgets, savings goals
├── expense_tracker/ # Project settings and root URL routing
├── static/          # Global CSS assets
├── templates/       # Django templates
├── seed_data.py     # Seeds default global categories
├── manage.py        # Django management entrypoint
├── requirements.txt # Direct Python dependencies
└── db.sqlite3       # Local development database
```

## URLs

- `/` dashboard
- `/auth/signup/`, `/auth/login/`, `/auth/logout/`, `/auth/profile/`, `/auth/password-change/`
- `/categories/`, `/income/`, `/expenses/`, `/budgets/`, `/savings/`
- `/analytics/dashboard/`, `/analytics/api/chart-data/`, `/analytics/ai-insights/`, `/analytics/reports/`, `/analytics/reports/export/`
- `/admin/`

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run migrations with `python manage.py migrate`.
4. Seed the default categories with `python seed_data.py`.
5. Create an admin user with `python manage.py createsuperuser`.
6. Start the server with `python manage.py runserver`.

Then open `http://127.0.0.1:8000/`.

## Tests

Run the test suite with:

```bash
python manage.py test
```

The existing tests cover user profile creation, authentication views, category and transaction flows, budget calculations, and savings goal completion logic.
