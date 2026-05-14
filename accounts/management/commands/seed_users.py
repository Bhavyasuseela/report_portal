"""
Management command to seed initial users.
Usage: python manage.py seed_users

ROLE STRUCTURE:
  - Admin: nirajan.kondapalli@ncmrwf.gov.in  (created via createsuperuser OR auto-seeded)
  - Conveners:
      Dr. Kondapalli Niranjan Kumar  niranjan@ncmrwf.gov.in   (convener + reviewer + author)
      Dr. S. Indira Rani             indrani@ncmrwf.gov.in    (convener + reviewer + author, Chairman)
  - Reviewers: All scientists — also granted author access via extra_roles
  - Librarian: librarian@ncmrwf.gov.in
  - Head (Director): director@ncmrwf.gov.in

SELF-ASSIGNMENT BLOCK:
  Niranjan and Indrani CANNOT assign reports to themselves (enforced in views.py).

MULTI-ROLE LOGIN:
  - Reviewers can log in as Author (extra_roles='author')
  - Conveners can log in as Author or Reviewer (extra_roles='author,reviewer')
"""
from django.core.management.base import BaseCommand
from accounts.models import User

REVIEWERS = [
    ("Dr. V.S. Prasad",                  "vsprasad@ncmrwf.gov.in",                 "Scientist - G"),
    ("Dr. John P. George",               "john@ncmrwf.gov.in",                      "Scientist - G"),
    ("Dr. Preveen Kumar",                "preveen@ncmrwf.gov.in",                   "Scientist - G"),
    ("Dr. Saji Mohandas",                "saji@ncmrwf.gov.in",                      "Scientist - G"),
    ("Dr. Raghavendra Ashrit",           "ashrit@ncmrwf.gov.in",                    "Scientist - G"),
    ("Dr. Ashish Routray",               "ashishroutray@ncmrwf.gov.in",             "Scientist - G"),
    ("Dr. S.Indira Rani",                "indira@ncmrwf.gov.in",                    "Scientist - F"),
    ("Dr. A.Jayakumar",                  "jkumar@ncmrwf.gov.in",                    "Scientist - F"),
    ("Dr. D.K.Mahapatra",                "debasis@ncmrwf.gov.in",                   "Scientist - E"),
    ("Dr. Imranali M. Momin",            "imranali@ncmrwf.gov.in",                  "Scientist - E"),
    ("Dr. Anurose T.J.",                 "anurose@ncmrwf.gov.in",                   "Scientist - E"),
    ("Dr. Gibies George",                "gibies@ncmrwf.gov.in",                    "Scientist - E"),
    ("Dr. Sumit Kumar",                  "sumit@ncmrwf.gov.in",                     "Scientist - E"),
    ("Dr. Ashu Mamgain",                 "amamgain@ncmrwf.gov.in",                  "Scientist - E"),
    ("Dr. Akhilesh Kumar Mishra",        "akhilesh@ncmrwf.gov.in",                  "Scientist - E"),
    ("Dr. Suryakanti Dutta",             "surya@ncmrwf.gov.in",                     "Scientist - E"),
    ("Dr. Mohana. S. Thota",             "mohant@ncmrwf.gov.in",                    "Scientist - E"),
    ("Dr. Hashmi Fatima",                "hashmi@ncmrwf.gov.in",                    "Scientist - E"),
    ("Mr. Ankur Gupta",                  "ankur@ncmrwf.gov.in",                     "Scientist - D"),
    ("Dr. Devajyoti Dutta",              "djyoti@ncmrwf.gov.in",                    "Scientist - D"),
    ("Dr. Srinivas Desamsetti",          "srinivas@ncmrwf.gov.in",                  "Scientist - D"),
    ("Dr. B.R.R Hari Prasad Kottu",      "hari@ncmrwf.gov.in",                      "Scientist - D"),
    ("Dr. Upal Saha",                    "upal@ncmrwf.gov.in",                      "Scientist - C"),
    ("Dr. V.S Ramarao Mandavilli",       "ramarao@ncmrwf.gov.in",                   "Scientist - C"),
    ("Dr. Devanil Choudhury",            "devanil@ncmrwf.gov.in",                   "Scientist - C"),
    ("Dr. Durgesh Nandan Piyush",        "durgesh@ncmrwf.gov.in",                   "Scientist - C"),
    ("Dr. Abhishek Lodh",                "abhishek.lodh@ncmrwf.gov.in",             "Scientist - C"),
    ("Dr. Mansi Bhowmick",               "mansi@ncmrwf.gov.in",                     "Project Scientist- III"),
    ("Dr. Shweta Bhati",                 "shweta@ncmrwf.gov.in",                    "Project Scientist- III"),
    ("Dr. Dineshkumar Kevalji Sankhala", "dinesh@ncmrwf.gov.in",                    "Project Scientist- III"),
    ("Dr. Greeshma M Mohan",             "greeshma@ncmrwf.gov.in",                  "Project Scientist- III"),
    ("Dr. M.Venkatarami Reddy",          "venkat@ncmrwf.gov.in",                    "Project Scientist- III"),
    ("Mr. Harvir Singh",                 "harvir@ncmrwf.gov.in",                    "Project Scientist- III"),
    ("Dr. Sushant Kumar",                "sushant@ncmrwf.gov.in",                   "Project Scientist- III"),
    ("Ms. Neha Rajput Mangalsingh",      "neharajput@ncmrwf.gov.in",                "Project Scientist- II"),
    ("Ms. Shivali Gangwar",              "shivalig@ncmrwf.gov.in",                  "Project Scientist- II"),
    ("Dr. Lokesh Pandey",                "lkpandey@ncmrwf.gov.in",                  "Project Scientist- II"),
    ("Dr. Chollangi Sridevi",            "sridevi@ncmrwf.gov.in",                   "Project Scientist- II"),
    ("Mr. Suraj Ravindran",              "suraj@ncmrwf.gov.in",                     "Project Scientist- II"),
    ("Dr. Nishtha Agrawal",              "nishtha@ncmrwf.gov.in",                   "Project Scientist- II"),
    ("Dr. Deepak Singh Bisht",           "dsbisht@ncmrwf.gov.in",                   "Project Scientist- II"),
    ("Dr. Shubha",                       "shubha@ncmrwf.gov.in",                    "Project Scientist- II"),
    ("Dr. Nagarjuna Rao D.",             "dgnrao@ncmrwf.gov.in",                    "Project Scientist- II"),
    ("Dr. Sukhwinder Kaur",              "sukhwinder@ncmrwf.gov.in",                "Project Scientist- II"),
    ("Mr. Bibhuti Sharan Keshav",        "keshavbs@ncmrwf.gov.in",                  "Project Scientist- II"),
    ("Mr. Ashutosh Kumar Sinha",         "ashutosh@ncmrwf.gov.in",                  "Project Scientist- II"),
    ("Dr. Kumarjit Saha",                "kumarjit@ncmrwf.gov.in",                  "Project Scientist- II"),
    ("Dr. Navin Chandra",                "navin@ncmrwf.gov.in",                     "Project Scientist- II"),
    ("Azad Singh Rajpoot",               "asrajpoot@ncmrwf.gov.in",                 "Project Scientist- II"),
    ("Mr. Abhijit V.",                   "abhi@ncmrwf.gov.in",                      "Project Scientist- II"),
    ("Dr. Gauri Shanker",                "gauri@ncmrwf.gov.in",                     "Project Scientist- II"),
    ("Ezhilarasi S",                     "ezhilarasi.s@ncmrwf.gov.in",              "Project Scientist- II"),
    ("Smrati Purwar",                    "smrati.purwar@ncmrwf.gov.in",             "Project Scientist- II"),
    ("Smrutishree Lenka",                "smruti.swati@ncmrwf.gov.in",              "Project Scientist- II"),
    ("Jivesh Dixit",                     "j.dixit@ncmrwf.gov.in",                   "Project Scientist- II"),
    ("Donali Gogoi",                     "donali.gogoi@ncmrwf.gov.in",              "Project Scientist- II"),
    ("Rehan Hossain",                    "rehan.hossain@ncmrwf.gov.in",             "Project Scientist- II"),
    ("Sanjiban Roy",                     "sanjiban.roy@ncmrwf.gov.in",              "Project Scientist- II"),
    ("Joydeb Saha",                      "joydeb.saha@ncmrwf.gov.in",               "Project Scientist- II"),
    ("Aman Fatima",                      "aman.fatima@ncmrwf.gov.in",               "Project Scientist- I"),
    ("Md Amjad Ali",                     "amjad.ali05@ncmrwf.gov.in",               "Project Scientist- I"),
]
class Command(BaseCommand):
    help = 'Seed initial users: admin, conveners, reviewers, librarian, head'

    def handle(self, *args, **options):
        DEFAULT_PASSWORD = 'NCMRWF@2024'

        # ── Admin ─────────────────────────────────────────────────────────────
        # Admin is the superuser. Created via createsuperuser OR auto-seeded here.
        admin_email = 'nirajan.kondapalli@ncmrwf.gov.in'
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                password=DEFAULT_PASSWORD,
                full_name='Nirajan Kondapalli (Admin)',
            )
            self.stdout.write(self.style.SUCCESS(f'  Created admin (superuser): {admin_email}'))
        else:
            # Ensure existing record has admin role
            admin_user = User.objects.get(email=admin_email)
            if admin_user.role != 'admin':
                admin_user.role = 'admin'
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save()
            self.stdout.write(f'  Admin exists: {admin_email}')

        # ── Conveners ─────────────────────────────────────────────────────────
        # Both conveners can also log in as reviewer and author (extra_roles)
        # Neither can assign a report to themselves (enforced in assign_reviewer view)
        conveners = [
            ('Dr. Kondapalli Niranjan Kumar', 'niranjan@ncmrwf.gov.in'),   # Convener
            ('Dr. S. Indira Rani',            'indrani@ncmrwf.gov.in'),    # Chairman
        ]
        for name, email in conveners:
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email, password=DEFAULT_PASSWORD,
                    full_name=name, role='convener',
                    extra_roles='reviewer,author',
                )
                self.stdout.write(self.style.SUCCESS(f'  Created convener: {email}'))
            else:
                # Ensure extra_roles is set
                u = User.objects.get(email=email)
                if 'author' not in u.extra_roles or 'reviewer' not in u.extra_roles:
                    u.extra_roles = 'reviewer,author'
                    u.save()
                self.stdout.write(f'  Convener exists: {email}')

        # ── Reviewers ─────────────────────────────────────────────────────────
        # All reviewers also get author access (extra_roles='author')
        # Niranjan is already in REVIEWERS list naturally via his convener record
        created = skipped = 0
        for full_name, email, designation in REVIEWERS:
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    password=DEFAULT_PASSWORD,
                    full_name=f'{full_name} ({designation})',
                    role='reviewer',
                    extra_roles='author',
                )
                created += 1
            else:
                # Ensure existing reviewers have author extra_role
                u = User.objects.get(email=email)
                if 'author' not in u.extra_roles:
                    u.extra_roles = 'author' if not u.extra_roles else u.extra_roles + ',author'
                    u.save()
                skipped += 1
        self.stdout.write(self.style.SUCCESS(
            f'  Reviewers: {created} created, {skipped} already existed'))

        # ── Librarian ─────────────────────────────────────────────────────────
        lib_email = 'library@ncmrwf.gov.in'
        if not User.objects.filter(email=lib_email).exists():
            User.objects.create_user(
                email=lib_email, password=DEFAULT_PASSWORD,
                full_name='NCMRWF Librarian', role='librarian',
            )
            self.stdout.write(self.style.SUCCESS(f'  Created librarian: {lib_email}'))
        else:
            self.stdout.write(f'  Librarian exists: {lib_email}')

        # ── Head / Director ───────────────────────────────────────────────────
        head_email = 'director@ncmrwf.gov.in'
        if not User.objects.filter(email=head_email).exists():
            User.objects.create_user(
                email=head_email, password=DEFAULT_PASSWORD,
                full_name='Director, NCMRWF', role='head',
            )
            self.stdout.write(self.style.SUCCESS(f'  Created head/director: {head_email}'))
        else:
            self.stdout.write(f'  Head exists: {head_email}')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Default password for all seeded accounts: {DEFAULT_PASSWORD}'))
