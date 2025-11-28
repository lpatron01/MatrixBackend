
## CORS Configuration

The API supports Cross-Origin Resource Sharing (CORS) for the following origins (configured in `.env`):
- `http://localhost:3000`
- `http://127.0.0.1:3000`

---

## Environment Variables

Key environment variables (see `.env` file):

```bash
# Django settings
DEBUG=True
SECRET_KEY=django-insecure-change-me
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://postgres:2025@localhost:5432/hack

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@example.com
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- PostgreSQL database

### Installation Steps

1. **Create virtual environment:**
```bash
python -m venv .venv
```

2. **Activate virtual environment:**
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
# Copy and edit .env file with your settings
cp .env.example .env
```

5. **Run migrations:**
```bash
python manage.py migrate
```

6. **Create superuser (optional):**
```bash
python manage.py createsuperuser
```

7. **Run development server:**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

---

## Admin Panel

Django admin panel is available at `/admin/` for staff users.

---

