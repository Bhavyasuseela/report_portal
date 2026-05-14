# MySQL Setup Guide

## Overview of Database Handling

This project uses **Django ORM** as the database abstraction layer.
All database access goes through Django models defined in:
- `accounts/models.py` — User model (authentication, roles, OTP)
- `reports/models.py` — Report model (submissions, reviews, workflow)

Django translates Python model code into SQL automatically, so the same
codebase works on SQLite (dev) and MySQL (production) with only a settings
change.

---

## How the Database Is Handled

| Layer | What it does |
|---|---|
| `models.py` | Defines tables as Python classes |
| `migrations/` | Tracks schema changes; applied with `migrate` |
| `settings.py DATABASES` | Selects the database engine and credentials |
| Django ORM | Translates `Model.objects.filter(...)` → SQL queries |
| `mysqlclient` | Low-level Python driver that talks to MySQL |

---

## Step 1 — Install MySQL Server

### Ubuntu / Debian
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

### macOS (Homebrew)
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

### Windows
Download MySQL Community Server from https://dev.mysql.com/downloads/

---

## Step 2 — Create the Database and User

Log into MySQL as root:
```bash
mysql -u root -p
```

Run these SQL commands:
```sql
CREATE DATABASE reportportal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'reportportal_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON reportportal_db.* TO 'reportportal_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## Step 3 — Install Python MySQL Driver

```bash
# Ubuntu/Debian — requires libmysqlclient-dev
sudo apt install libmysqlclient-dev python3-dev
pip install mysqlclient

# macOS
brew install mysql-client
pip install mysqlclient

# Windows (if mysqlclient fails, use PyMySQL as fallback)
pip install PyMySQL
```

**If using PyMySQL** add this to `reportportal/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

## Step 4 — Configure Environment Variables

Set these before starting the server (or add to a `.env` file):

```bash
export DB_NAME=reportportal_db
export DB_USER=reportportal_user
export DB_PASSWORD=your_strong_password
export DB_HOST=localhost
export DB_PORT=3306

# Optional — encrypts PDF filenames shown on frontend
export PDF_FILENAME_SECRET=change-this-to-a-long-random-string
```

Or edit `reportportal/settings.py` directly for local development (not
recommended for production).

---

## Step 5 — Run Migrations

```bash
cd reportportal_fixed
python manage.py migrate
```

This creates all tables in MySQL automatically.

---

## Step 6 — Create the Admin Superuser

```bash
python manage.py createsuperuser
```

Enter an email and password. This user will have `is_staff=True` and
can log in at `/admin-panel/` to manage all users.

Alternatively, use the seed script to populate test users:
```bash
python manage.py seed_users
```

---

## Step 7 — Start the Server

```bash
python manage.py runserver
```

Then visit http://localhost:8000

---

## PDF Filename Encryption — How It Works

When a user uploads a PDF, the **real filename is stored in the MySQL
database** in the `paper_doc`, `plagiarism_doc`, or
`reviewer_attachment` columns exactly as Django saves it.

On the **frontend**, file links are replaced with encrypted tokens:

```
/file/aGVsbG8td29ybGQ.pdf   ← what the browser sees
```

Instead of:

```
/media/papers/climate_model_report_final_v2.pdf   ← real path (hidden)
```

The encryption is XOR cipher with a SHA-256 key derived from
`PDF_FILENAME_SECRET`, then base64url-encoded. When a user clicks
the link, Django's `serve_encrypted_pdf` view decrypts the token,
looks up the real file on disk, and streams it — without ever
revealing the actual filename to the browser.

**Backend database column still holds the real path** so the file can
always be recovered even if the secret changes (just re-encrypt links
at runtime).

---

## Troubleshooting

| Error | Fix |
|---|---|
| `django.db.utils.OperationalError: (2002)` | MySQL not running — `sudo systemctl start mysql` |
| `django.db.utils.OperationalError: Access denied` | Wrong DB_USER / DB_PASSWORD |
| `ImportError: No module named 'MySQLdb'` | `pip install mysqlclient` |
| `django.db.utils.ProgrammingError: Table doesn't exist` | Run `python manage.py migrate` |
