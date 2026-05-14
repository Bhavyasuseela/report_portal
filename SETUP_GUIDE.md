# ReportPortal — Complete Setup Guide

## STEP 1: Install Python & Django
Make sure Python 3.10+ is installed.

```bash
pip install -r requirements.txt
```

---

## STEP 2: Configure Email (IMPORTANT)

Open `reportportal/settings.py` and update these lines:

```python
EMAIL_HOST_USER = 'your-gmail@gmail.com'
EMAIL_HOST_PASSWORD = 'your-gmail-app-password'
DEFAULT_FROM_EMAIL = 'ReportPortal <your-gmail@gmail.com>'
```

### How to get Gmail App Password:
1. Go to your Google Account → Security
2. Enable 2-Step Verification
3. Go to Security → App Passwords
4. Select "Mail" and your device → click Generate
5. Copy the 16-character password into EMAIL_HOST_PASSWORD

---

## STEP 3: Run Migrations

```bash
cd reportportal
python manage.py makemigrations accounts
python manage.py makemigrations reports
python manage.py migrate
```

---

## STEP 4: Create Superuser (for admin panel)

```bash
python manage.py createsuperuser
# Enter email, password when prompted
```

---

## STEP 5: Seed Initial Users

```bash
python manage.py seed_users
```


**IMPORTANT**: Change emails to real emails so OTP can be delivered!

---

## STEP 6: Update Emails in Admin Panel

1. Run the server: `python manage.py runserver`
2. Go to: http://127.0.0.1:8000/admin/
3. Log in with your superuser account
4. Click **Accounts > Users**
5. Edit each user and change their email to a real working email

---

## STEP 7: Start the Server

```bash
python manage.py runserver
```

Open: http://127.0.0.1:8000/

---

## How to Add New Users

### Option A: Admin Panel
1. Go to http://127.0.0.1:8000/admin/
2. Accounts → Users → Add User
3. Enter email, set password, choose role (author/convener/reviewer)

### Option B: Django Shell
```python
python manage.py shell

from accounts.models import User
User.objects.create_user(
    email='newreviewer@example.com',
    password='Portal@2024',
    full_name='Dr. New Person',
    role='reviewer'  # or 'author' or 'convener'
)
```

---

## Full URL Reference

| URL                              | Who uses it    | What it does                    |
|----------------------------------|----------------|---------------------------------|
| /login/                          | Everyone       | Login page                      |
| /verify-otp/                     | Everyone       | OTP verification                |
| /logout/                         | Everyone       | Logout                          |
| /author/                         | Author         | Author dashboard                |
| /author/submit/                  | Author         | Submit a new report             |
| /convener/                       | Convener       | All reports + stats             |
| /convener/report/<id>/           | Convener       | Report detail view              |
| /convener/assign/<id>/           | Convener       | Assign reviewer                 |
| /convener/status/<id>/           | Convener       | Update report status            |
| /reviewer/                       | Reviewer       | Assigned papers                 |
| /reviewer/review/<id>/           | Reviewer       | Submit review + feedback        |
| /admin/                          | Superuser      | Django admin panel              |

---

## Workflow Summary

1. **Author** logs in → submits report with type, title, abstract, keywords, documents
2. **Convener** receives email → opens dashboard → reads abstract → assigns to a reviewer
3. **Reviewer** receives email with abstract → downloads full paper → submits feedback + decision
4. **Convener** sees reviewer feedback → updates status (Accepted / Revision Required / Rejected)
5. **Author** receives status update email

---

## Project Folder Structure

```
reportportal/
├── manage.py
├── requirements.txt
├── reportportal/
│   ├── settings.py          ← configure email here
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py            ← User model with OTP
│   ├── views.py             ← login, OTP, logout
│   ├── urls.py
│   ├── admin.py
│   └── management/
│       └── commands/
│           └── seed_users.py
├── reports/
│   ├── models.py            ← Report model
│   ├── views.py             ← all dashboard views
│   ├── urls.py
│   └── admin.py
├── templates/
│   ├── base.html            ← main layout + CSS
│   ├── accounts/
│   │   ├── login.html
│   │   └── verify_otp.html
│   └── reports/
│       ├── author_dashboard.html
│       ├── submit_report.html
│       ├── convener_dashboard.html
│       ├── report_detail_convener.html
│       ├── assign_reviewer.html
│       ├── reviewer_dashboard.html
│       └── submit_review.html
└── media/                   ← uploaded files (auto-created)
    ├── papers/
    └── plagiarism/
```
