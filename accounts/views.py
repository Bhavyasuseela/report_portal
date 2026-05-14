from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from accounts.models import User
import requests


# ─── EMAIL API ────────────────────────────────────────────────────────────────
EMAIL_API_URL = "https://support.ncmrwf.gov.in/mail/api_send_email_reports"

def send_email_via_api(to_email, to_name, subject, html_body):
    """Send email via NCMRWF API with Django SMTP as fallback."""
    # Try the NCMRWF internal API first
    try:
        response = requests.post(
            EMAIL_API_URL,
            json={
                "to_email": to_email,
                "to_name": to_name,
                "subject": subject,
                "html_body": html_body,
            },
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if response.status_code == 200 and response.text.strip():
            return response.json()
        # API returned empty or non-200 — fall through to SMTP
        raise ValueError(f"API returned status {response.status_code} with empty body")
    except Exception as api_err:
        print(f"[EMAIL API UNAVAILABLE] to={to_email} error={api_err} — falling back to SMTP")

    # Fallback: Django SMTP (configured in settings.py)
    try:
        send_mail(
            subject=subject,
            message="Please view this email in an HTML-capable email client.",
            html_message=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        print(f"[EMAIL SMTP OK] to={to_email} subject={subject}")
        return {"status": "sent_via_smtp"}
    except Exception as smtp_err:
        print(f"[EMAIL SMTP ERROR] to={to_email} subject={subject} error={smtp_err}")
        return None

def send_email_to_many(recipients, subject, html_body):
    for recipient in recipients:
        if isinstance(recipient, tuple):
            to_email, to_name = recipient
        else:
            to_email = recipient
            to_name = recipient
        send_email_via_api(to_email, to_name, subject, html_body)
# ──────────────────────────────────────────────────────────────────────────────


ROLE_LABELS = {
    'author': 'Author',
    'convener': 'Convener',
    'reviewer': 'Reviewer',
    'librarian': 'Librarian',
    'head': 'Head',
    'admin': 'Admin',
}

ROLE_ICONS = {
    'author': 'bi-pencil-square',
    'convener': 'bi-folder2-open',
    'reviewer': 'bi-search',
    'librarian': 'bi-book',
    'head': 'bi-person-badge',
    'admin': 'bi-shield-lock',
}

# ── Specific person constraints ────────────────────────────────────────────────
# Niranjan is convener but CANNOT assign reports to himself
NIRANJAN_EMAIL = 'niranjan@ncmrwf.gov.in'
# Indrani is chairman/convener but CANNOT assign reports to herself
INDRANI_EMAIL = 'indrani@ncmrwf.gov.in'

# Admin email (superuser-created; also present in DB)
ADMIN_EMAIL = 'nirajan.kondapalli@ncmrwf.gov.in'

# Head email
HEAD_EMAIL = 'director@ncmrwf.gov.in'

# Allowed email domain for registration
ALLOWED_REGISTRATION_DOMAINS = ['ncmrwf.gov.in', 'govcontractor.in', 'nic.in']


def _do_login(request, role):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
            return render(request, 'accounts/login_role.html', {
                'role': role, 'role_label': ROLE_LABELS[role], 'role_icon': ROLE_ICONS[role]
            })

        # Check if user can access the requested role
        if not user.can_access_role(role):
            messages.error(request, f'This login page is only for {ROLE_LABELS[role]}s.')
            return render(request, 'accounts/login_role.html', {
                'role': role, 'role_label': ROLE_LABELS[role], 'role_icon': ROLE_ICONS[role]
            })

        # For self-registered authors: require admin approval
        if role == 'author' and not user.is_active:
            if not user.is_approved:
                messages.error(request, 'Your account is pending admin approval. Please wait for an administrator to approve your registration.')
            else:
                messages.error(request, 'Your account has been deactivated. Please contact the administrator.')
            return render(request, 'accounts/login_role.html', {
                'role': role, 'role_label': ROLE_LABELS[role], 'role_icon': ROLE_ICONS[role]
            })

        if not user.check_password(password):
            messages.error(request, 'Incorrect password.')
            return render(request, 'accounts/login_role.html', {
                'role': role, 'role_label': ROLE_LABELS[role], 'role_icon': ROLE_ICONS[role]
            })

        otp = user.generate_otp()
        result = send_email_via_api(
            to_email=user.email,
            to_name=user.full_name or user.email,
            subject=f'OTP-You are logging in as {ROLE_LABELS[role]}',
            html_body=f"""
<p>Hello <strong>{user.full_name or user.email}</strong>,</p>
<p>You are logging in to the <strong>Internal Report Submission Portal</strong> as: <strong>{ROLE_LABELS[role]}</strong></p>
<p>Your one-time password (OTP) is:</p>
<h2 style="letter-spacing:4px;">{otp}</h2>
<p>This OTP is valid for <strong>10 minutes</strong>. Do not share it with anyone.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )
        if result is None:
            messages.error(request, 'Failed to send OTP email. Please try again.')
            return render(request, 'accounts/login_role.html', {
                'role': role, 'role_label': ROLE_LABELS[role], 'role_icon': ROLE_ICONS[role]
            })

        request.session['otp_user_id'] = user.id
        request.session['otp_intended_role'] = role
        messages.success(request, f'OTP sent to {email}. You are logging in as {ROLE_LABELS[role]}.')
        return redirect('verify_otp')

    return render(request, 'accounts/login_role.html', {
        'role': role,
        'role_label': ROLE_LABELS[role],
        'role_icon': ROLE_ICONS[role],
    })


def login_author(request):
    return _do_login(request, 'author')


def login_convener(request):
    return _do_login(request, 'convener')


def login_reviewer(request):
    return _do_login(request, 'reviewer')


def login_librarian(request):
    return _do_login(request, 'librarian')


def login_head(request):
    return _do_login(request, 'head')


def login_admin(request):
    if request.user.is_authenticated:
        active_role = request.session.get('active_role', request.user.role)
        if active_role == 'admin' or request.user.role == 'admin':
            return redirect('admin_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No admin account found with this email.')
            return render(request, 'accounts/admin_login.html')

        if user.role != 'admin':
            messages.error(request, 'This login is restricted to Admin accounts only.')
            return render(request, 'accounts/admin_login.html')

        if not user.check_password(password):
            messages.error(request, 'Incorrect password.')
            return render(request, 'accounts/admin_login.html')

        otp = user.generate_otp()
        result = send_email_via_api(
            to_email=user.email,
            to_name=user.full_name or user.email,
            subject='Admin Login OTP – Report Portal',
            html_body=f"""
<p>Hello <strong>{user.full_name or user.email}</strong>,</p>
<p>You are logging in as <strong>Admin</strong> on the Internal Report Submission Portal.</p>
<p>Your OTP is:</p>
<h2 style="letter-spacing:4px;">{otp}</h2>
<p>Valid for <strong>10 minutes</strong>. Do not share it with anyone.</p>
<br><p>— Internal Report Submission Portal</p>
""",
        )
        if result is None:
            messages.error(request, 'Failed to send OTP. Please try again.')
            return render(request, 'accounts/admin_login.html')

        request.session['otp_user_id'] = user.id
        request.session['otp_intended_role'] = 'admin'
        messages.success(request, f'OTP sent to {email}.')
        return redirect('verify_otp')

    return render(request, 'accounts/admin_login.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/login.html')


def register_author(request):
    """
    Public registration — any email is allowed.
    After registration the account is INACTIVE (is_approved=False, is_active=False)
    and must be approved by an admin before the author can log in.
    On approval the admin sends a login email to the author.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        designation = request.POST.get('designation', '').strip()
        department = request.POST.get('department', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not all([first_name, last_name, email, password, confirm_password]):
            messages.error(request, 'First name, last name, email, and password fields are required.')
            return render(request, 'accounts/register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'accounts/register.html')

        # Basic email format check
        if '@' not in email or '.' not in email.split('@')[-1]:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'accounts/register.html')

        full_name = f'{first_name} {last_name}'.strip()
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            first_name=first_name,
            last_name=last_name,
            designation=designation,
            department=department,
            role='author',
            must_reset_password=False,
            is_active=False,       # disabled until admin approves
            is_approved=False,
        )

        # Notify admin(s) about the new registration
        admin_users = User.objects.filter(role='admin')
        for admin in admin_users:
            send_email_via_api(
                to_email=admin.email,
                to_name=admin.full_name or admin.email,
                subject='New Author Registration — Approval Required',
                html_body=f"""
<p>Hello <strong>{admin.full_name or admin.email}</strong>,</p>
<p>A new author has registered on the <strong>Internal Report Submission Portal</strong> and is awaiting your approval.</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Name</strong></td><td>{full_name}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Email</strong></td><td>{email}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Designation</strong></td><td>{designation or '—'}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Department</strong></td><td>{department or '—'}</td></tr>
</table>
<p>Please log in to the Admin Dashboard to approve or reject this registration.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )

        messages.success(
            request,
            'Registration successful! Your account is pending admin approval. '
            'You will receive an email with login instructions once an administrator approves your account.'
        )
        return redirect('login_author')

    return render(request, 'accounts/register.html')


@ensure_csrf_cookie
def verify_otp_view(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        if user.verify_otp(entered_otp):
            user.clear_otp()
            del request.session['otp_user_id']
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            intended_role = request.session.pop('otp_intended_role', user.role)
            request.session['active_role'] = intended_role

            role_label = ROLE_LABELS.get(intended_role, intended_role.capitalize())
            messages.success(request, f'Welcome, {user.full_name or user.email}! You are logged in as {role_label}.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')

    return render(request, 'accounts/verify_otp.html', {'user_email': user.email})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


def dashboard_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')

    active_role = request.session.get('active_role', request.user.role)

    if active_role == 'admin':
        return redirect('admin_dashboard')
    elif active_role == 'convener':
        return redirect('convener_dashboard')
    elif active_role == 'author':
        return redirect('author_dashboard')
    elif active_role == 'reviewer':
        return redirect('reviewer_dashboard')
    elif active_role == 'librarian':
        return redirect('librarian_dashboard')
    elif active_role == 'head':
        return redirect('head_dashboard')
    return redirect('login')


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_admin')
        active_role = request.session.get('active_role', request.user.role)
        if request.user.role != 'admin' and active_role != 'admin':
            messages.error(request, 'Admin access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    from reports.models import Report

    users = User.objects.exclude(role='admin').order_by('role', 'email')

    stats = {
        'total_users': users.count(),
        'authors': users.filter(role='author').count(),
        'conveners': users.filter(role='convener').count(),
        'reviewers': users.filter(role='reviewer').count(),
        'librarians': users.filter(role='librarian').count(),
        'heads': users.filter(role='head').count(),
        'active_users': users.filter(is_active=True).count(),
        'total_reports': Report.objects.count(),
        'pending_authors': users.filter(role='author', is_approved=False).count(),
    }

    conveners = users.filter(role='convener')
    reviewers = users.filter(role='reviewer')
    authors = users.filter(role='author')
    librarians = users.filter(role='librarian')
    heads = users.filter(role='head')

    manageable_roles = [r for r in User.ROLE_CHOICES if r[0] != 'admin']

    return render(request, 'accounts/admin_dashboard.html', {
        'users': users,
        'stats': stats,
        'conveners': conveners,
        'reviewers': reviewers,
        'authors': authors,
        'librarians': librarians,
        'heads': heads,
        'role_choices': manageable_roles,
    })


@admin_required
def admin_add_user(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        role = request.POST.get('role', 'author')
        password = request.POST.get('password', '').strip()

        if not all([full_name, email, role, password]):
            messages.error(request, 'All fields are required.')
            return redirect('admin_dashboard')

        if role == 'admin':
            messages.error(request, 'Admin accounts must be created via createsuperuser command.')
            return redirect('admin_dashboard')

        if User.objects.filter(email=email).exists():
            messages.error(request, f'User with email {email} already exists.')
            return redirect('admin_dashboard')

        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            role=role,
        )

        # If reviewer or convener, also grant author role
        if role in ('reviewer', 'convener'):
            user.extra_roles = 'author'
            user.save()

        role_dashboard = {
            'reviewer': 'Reviewer Dashboard',
            'convener': 'Convener Dashboard',
            'librarian': 'Librarian Dashboard',
            'head': 'Head Dashboard',
            'author': 'Author Dashboard',
        }
        dash_label = role_dashboard.get(role, 'Dashboard')

        send_email_via_api(
            to_email=email,
            to_name=full_name,
            subject='Welcome to the Internal Report Submission Portal — Your Login Details',
            html_body=f"""
<p>Dear <strong>{full_name}</strong>,</p>
<p>An account has been created for you on the <strong>Internal Report Submission Portal</strong>.</p>
<p>You can log in to your <strong>{dash_label}</strong> using the following credentials:</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Email</strong></td><td>{email}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Password</strong></td><td>{password}</td></tr>
</table>
<p style="color:red;"><strong>IMPORTANT:</strong> After logging in, you MUST change your password immediately.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )

        messages.success(request, f'User {email} ({role}) created successfully. Login details emailed.')
    return redirect('admin_dashboard')


@admin_required
def admin_edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.role == 'admin':
        messages.error(request, 'Admin accounts cannot be edited here.')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        user.full_name = request.POST.get('full_name', user.full_name).strip()
        new_role = request.POST.get('role', user.role)
        if new_role != 'admin':
            user.role = new_role
        user.is_active = request.POST.get('is_active') == 'on'
        new_password = request.POST.get('new_password', '').strip()
        if new_password:
            user.set_password(new_password)
        # Auto-grant author role for reviewer/convener
        if new_role in ('reviewer', 'convener'):
            roles = [r.strip() for r in user.extra_roles.split(',') if r.strip()]
            if 'author' not in roles:
                roles.append('author')
            user.extra_roles = ','.join(roles)
        user.save()
        messages.success(request, f'User {user.email} updated.')
    return redirect('admin_dashboard')


@admin_required
def admin_delete_user(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            if user.role == 'admin':
                messages.error(request, 'Admin accounts cannot be deleted here.')
            elif user == request.user:
                messages.error(request, 'You cannot delete your own account.')
            else:
                email = user.email
                user.delete()
                messages.success(request, f'User {email} deleted.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    return redirect('admin_dashboard')


@admin_required
def admin_toggle_active(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            if user.role == 'admin':
                messages.error(request, 'Admin accounts cannot be toggled here.')
            else:
                user.is_active = not user.is_active
                user.save()
                state = 'activated' if user.is_active else 'deactivated'
                messages.success(request, f'User {user.email} {state}.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    return redirect('admin_dashboard')


@admin_required
def admin_approve_author(request, user_id):
    """Approve a self-registered author so they can log in, then email them login instructions."""
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id, role='author')
            user.is_approved = True
            user.is_active = True
            user.save()

            login_url = request.build_absolute_uri('/login/author/')
            send_email_via_api(
                to_email=user.email,
                to_name=user.full_name or user.email,
                subject='Your Author Registration Has Been Approved — Login Details',
                html_body=f"""
<p>Dear <strong>{user.full_name or user.email}</strong>,</p>
<p>Your author registration on the <strong>Internal Report Submission Portal</strong> has been
<strong style="color:green;">approved</strong> by an administrator.</p>
<p>You can now log in to the Author Dashboard using the details below:</p>
<table style="border-collapse:collapse;margin:12px 0;">
  <tr><td style="padding:6px 16px 6px 0;"><strong>Login Page</strong></td>
      <td><a href="{login_url}">{login_url}</a></td></tr>
  <tr><td style="padding:6px 16px 6px 0;"><strong>Email</strong></td>
      <td>{user.email}</td></tr>
  <tr><td style="padding:6px 16px 6px 0;"><strong>Password</strong></td>
      <td>The password you set during registration.</td></tr>
</table>
<p style="color:#b45309;"><strong>Note:</strong> A One-Time Password (OTP) will be sent to this email address each time you log in for security verification.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )
            messages.success(request, f'Author {user.email} has been approved. Login instructions emailed.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    return redirect('admin_dashboard')


@admin_required
def admin_reject_author(request, user_id):
    """Reject (and delete) a self-registered author who has not been approved."""
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id, role='author', is_approved=False)
            email = user.email
            send_email_via_api(
                to_email=user.email,
                to_name=user.full_name or user.email,
                subject='Your Author Registration Was Not Approved',
                html_body=f"""
<p>Dear <strong>{user.full_name or user.email}</strong>,</p>
<p>We regret to inform you that your author registration on the <strong>Internal Report Submission Portal</strong> has not been approved at this time.</p>
<p>Please contact the portal administrator for further information.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )
            user.delete()
            messages.success(request, f'Registration for {email} has been rejected and removed.')
        except User.DoesNotExist:
            messages.error(request, 'User not found or already approved.')
    return redirect('admin_dashboard')


@login_required
def change_password(request):
    from django.contrib.auth import update_session_auth_hash

    is_first_time = request.user.must_reset_password

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        old_password = request.POST.get('old_password', '').strip()

        if not new_password or not confirm_password:
            messages.error(request, 'Please fill in all required fields.')
        elif not is_first_time and not old_password:
            messages.error(request, 'Please enter your current password.')
        elif not is_first_time and not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            request.user.set_password(new_password)
            request.user.must_reset_password = False
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password updated successfully!')
            return redirect('dashboard')

    return render(request, 'accounts/change_password.html', {
        'is_first_time': is_first_time,
    })


def forgot_password(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        try:
            user = User.objects.get(email=email)
            token = user.generate_password_reset_token()
            reset_url = request.build_absolute_uri(f'/reset-password/{token}/')
            result = send_email_via_api(
                to_email=user.email,
                to_name=user.full_name or user.email,
                subject='Password Reset-Internal Report Submission Portal',
                html_body=f"""
<p>Hello <strong>{user.full_name or user.email}</strong>,</p>
<p>Click the link below to reset your password (valid for <strong>1 hour</strong>):</p>
<p style="text-align:center; margin-top:20px;">
  <a href="{reset_url}" style="background-color:#2563eb; color:white; padding:12px 24px; text-decoration:none; border-radius:6px; font-weight:bold; display:inline-block;">
    Reset My Password
  </a>
</p>
<p>If you did not request this, please ignore this email.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )
            if result is None:
                messages.error(request, 'Failed to send reset email. Please contact the administrator.')
                return render(request, 'accounts/forgot_password.html')
        except User.DoesNotExist:
            pass

        messages.success(request, 'If that email is registered, a password reset link has been sent.')
        return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')


def reset_password_via_link(request, token):
    if request.user.is_authenticated:
        from django.contrib.auth import logout as auth_logout
        auth_logout(request)

    try:
        user = User.objects.get(password_reset_token=token)
    except User.DoesNotExist:
        messages.error(request, 'This password reset link is invalid or has already been used.')
        return redirect('forgot_password')

    if not user.verify_password_reset_token(token):
        messages.error(request, 'This password reset link has expired. Please request a new one.')
        return redirect('forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not new_password or not confirm_password:
            messages.error(request, 'Please fill in both fields.')
        elif new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            user.set_password(new_password)
            user.must_reset_password = False
            user.clear_password_reset_token()
            user.save()
            messages.success(request, 'Password reset successfully! You can now log in.')
            return redirect('login')

    return render(request, 'accounts/reset_password_via_link.html', {'token': token})
