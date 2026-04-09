# PythonAnywhere Deployment (Free Tier)

This guide deploys this Django project to PythonAnywhere using the free plan.

## 1. Prerequisites

- GitHub repo: https://github.com/DarpitParikh/CAMPS
- PythonAnywhere account

## 2. Create Web App on PythonAnywhere

1. Sign in to PythonAnywhere.
2. Go to **Web** tab.
3. Click **Add a new web app**.
4. Choose:
   - **Manual configuration**
   - Python version available on PythonAnywhere (prefer 3.10 or 3.11)

## 3. Clone and install dependencies

Open a **Bash** console on PythonAnywhere and run:

```bash
git clone https://github.com/DarpitParikh/CAMPS.git
cd CAMPS
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements_clean.txt
```

## 4. Create environment file

Create `.env` in project root (`/home/<username>/CAMPS/.env`):

```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_ALLOWED_HOSTS=<username>.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://<username>.pythonanywhere.com
```

You can generate a secure key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 5. Run Django setup commands

Still inside the activated venv:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 6. Configure WSGI on PythonAnywhere

In **Web** tab:

1. Set **Virtualenv** path:
   `/home/<username>/CAMPS/.venv`
2. Open WSGI configuration file and use:

```python
import os
import sys

path = '/home/<username>/CAMPS'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examhall.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 7. Static and media mapping

In **Web** tab -> **Static files**:

- URL: `/static/` -> Directory: `/home/<username>/CAMPS/staticfiles`
- URL: `/media/` -> Directory: `/home/<username>/CAMPS/media`

## 8. Reload

Click **Reload** on the Web tab.

Your app should be live at:
`https://<username>.pythonanywhere.com`

## 9. Update after code changes

When you push new commits to GitHub, run in PythonAnywhere Bash:

```bash
cd ~/CAMPS
source .venv/bin/activate
git pull
pip install -r requirements_clean.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then click **Reload** in the Web tab.

## Troubleshooting

- 400 Bad Request: check `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS`.
- Static not loading: re-check Static files mappings and run `collectstatic` again.
- Import/package error: verify virtualenv path in Web tab is `/home/<username>/CAMPS/.venv`.
- Check error log from **Web** tab -> **Error log**.
