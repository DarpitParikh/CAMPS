# CAMPS — Campus Academic Management and Planning System (CAMPS)

Welcome to CAMPS — a Django-based application for managing exam seating, allocations, attendance, results, and notices. This README gives a quick, attractive overview to get you started.

## Why CAMPS?

- Centralizes exam seat allocation, attendance tracking and results.
- Designed for universities and colleges needing reliable exam management.

## Key Features

- Seating allocation and student lists
- Notices and attachments management
- Result entry, reports and exports
- Faculty and student role-based access

## Quick Links

- [manage.py](manage.py#L1) — Django management entrypoint
- [examhall/settings.py](examhall/settings.py#L1) — Configuration
- `allocation/` — core app for allocation and related features

## Requirements

- Python 3.8+ (adjust to your environment)
- See `requirements.txt` for Python dependencies

## Quick Start (development)

1. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\Activate.ps1    # PowerShell
# or
venv\Scripts\activate.bat    # cmd.exe
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Apply database migrations

```powershell
python manage.py migrate
```

4. (Optional) Create a superuser

```powershell
python manage.py createsuperuser
```

5. Run the development server

```powershell
python manage.py runserver
# or use helper scripts: run_examhall.bat / run_examhall.ps1 / quickstart.bat
```

## Database

By default this project uses SQLite (`db.sqlite3` is included). For production, update `DATABASES` in [examhall/settings.py](examhall/settings.py#L1) to your preferred engine and run migrations.

## Static & Media

- Static files are served from `staticfiles/` after `collectstatic`.
- Uploaded attachments are stored in `media/notice_attachments/`.

Collect static files for production:

```powershell
python manage.py collectstatic --noinput
```

## Tests

Run the full test suite:

```powershell
python manage.py test
```

Run tests for the `allocation` app:

```powershell
python manage.py test allocation
```

## Deployment Notes

- See `PYTHONANYWHERE_DEPLOY.md` for a sample deployment walkthrough.
- Windows helper scripts: `run_examhall.bat`, `run_examhall.ps1`, `quickstart.bat`.

## Contributing

Contributions are welcome — open issues or send pull requests with clear descriptions and tests where appropriate. If you'd like, I can add a `CONTRIBUTING.md` with a PR checklist.

## License

See the project's `LICENSE` file for license details.

## Need More?

If you want I can:

- Expand deployment instructions for a specific host (e.g., Gunicorn + Nginx).
- Add `CONTRIBUTING.md`, `CHANGELOG.md`, or app-level READMEs.

Happy to adjust wording or add visuals/screenshots — tell me which sections to expand.
