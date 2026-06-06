# ExamHall — Exam Hall Management System

A Django-based application for managing exam seating, allocations, attendance, results, and notices.

## Key Features

- Seating allocation and student lists
- Notices and attachments management
- Result entry and reports
- Faculty and student authentication and role-specific views

## Requirements

- Python 3.8+ (use the version your environment requires)
- See `requirements.txt` for Python package dependencies

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
# or use included helper scripts: run_examhall.bat / run_examhall.ps1 / quickstart.bat
```

## Database

This project uses SQLite by default (`db.sqlite3` is included). For production, configure `DATABASES` in [examhall/settings.py](examhall/settings.py) and migrate accordingly.

## Static & Media

- Static files are served from `staticfiles/` in production when collected.
- Uploaded files (notices attachments) are stored under `media/notice_attachments/`.

To collect static files for production:

```powershell
python manage.py collectstatic --noinput
```

## Tests

Run the test suite with:

```powershell
python manage.py test
```

Or run tests for the `allocation` app specifically:

```powershell
python manage.py test allocation
```

## Deployment Notes

- See `PYTHONANYWHERE_DEPLOY.md` for an example deployment guide.
- There are helper scripts and shortcuts in the repository (`run_examhall.bat`, `run_examhall.ps1`, `quickstart.bat`) to simplify starting the app on Windows.

## Contributing

Contributions are welcome. Please open issues for bugs or feature requests and send pull requests with clear descriptions and tests where appropriate.

## License

This project includes a `LICENSE` file. Review it for licensing details.

## Useful Files

- `manage.py` — Django management entrypoint
- `requirements.txt` — Python dependencies
- `examhall/settings.py` — Django settings
- `allocation/` — core app for allocation and related features

If you want, I can expand any section (deployment, docs, API reference) or add a short CONTRIBUTING.md.
