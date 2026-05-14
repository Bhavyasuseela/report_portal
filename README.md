<<<<<<< HEAD
# report_portal_dashboard
Internal Report Submission Portal
=======
<<<<<<< HEAD
# report_portal
Internal Report Submission Portal
=======
# Internal Report Submission Portal — NCMRWF

A Django-based internal portal for managing academic and technical report submissions, peer review, and publication workflow.

## Quick Start

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_users      # creates conveners, reviewers, librarian
python manage.py runserver
```

Visit http://127.0.0.1:8000

## Default Credentials (after seed_users)

| Role      | Email                          | Password       |
|-----------|-------------------------------|----------------|
| Convener  | vupadhayayulab@gmail.com       | ncmrwf@2024    |
| Convener  | navyabhanothi@gmail.com        | ncmrwf@2024    |
| Librarian | librarian@ncmrwf.gov.in        | ncmrwf@2024    |
| Reviewers | (see seed_users.py for full list) | ncmrwf@2024 |

Authors self-register at /register/

## Changes in this version

- **Author self-registration**: Authors can register with name, email and password at /register/
- **Targeted convener notifications**: When author submits/resubmits, only the 2 designated conveners (Niranjan & Indirani) receive email
- **Dual-convener assign lock**: When one convener assigns a reviewer, the Assign button is disabled for the other convener to prevent duplicate assignments
- **Resubmitted reports tracking**: Resubmitted reports remain visible in the convener dashboard even after being accepted — use the "All Resubmitted (incl. Accepted)" filter
- **Full reviewer list**: All 61 NCMRWF reviewers pre-loaded via seed_users command
- **Portal renamed**: "Internal Report Submission Portal" throughout
- **Login page**: All 4 role cards now in a single row
>>>>>>> dae5e80 (Initial commit)
>>>>>>> 7125720 (Initial commit)
