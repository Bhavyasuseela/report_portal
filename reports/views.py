from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from reports.models import Report, SupportRequest, ResubmissionHistory
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
        raise ValueError(f"API returned status {response.status_code} with empty body")
    except Exception as api_err:
        print(f"[EMAIL API UNAVAILABLE] to={to_email} error={api_err} — falling back to SMTP")

    # Fallback: Django SMTP
    try:
        from django.core.mail import send_mail
        from django.conf import settings as django_settings
        send_mail(
            subject=subject,
            message="Please view this email in an HTML-capable email client.",
            html_message=html_body,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        print(f"[EMAIL SMTP OK] to={to_email} subject={subject}")
        return {"status": "sent_via_smtp"}
    except Exception as smtp_err:
        print(f"[EMAIL SMTP ERROR] to={to_email} subject={subject} error={smtp_err}")
        return None

def send_email_to_many(recipients, subject, html_body):
    """
    Send the same email to a list of (email, name) tuples or plain email strings.
    """
    for recipient in recipients:
        if isinstance(recipient, tuple):
            to_email, to_name = recipient
        else:
            to_email = recipient
            to_name = recipient
        send_email_via_api(to_email, to_name, subject, html_body)
# ──────────────────────────────────────────────────────────────────────────────

CONVENER_NOTIFY_EMAILS = [
    'niranjan@ncmrwf.gov.in',
    'indrani@ncmrwf.gov.in',
]

HEAD_EMAIL = 'director@ncmrwf.gov.in'

# Conveners who cannot assign reports to themselves
CONVENER_NO_SELF_ASSIGN = {
    'niranjan@ncmrwf.gov.in',
    'indrani@ncmrwf.gov.in',
}


def role_required(*roles):
    """
    Allows access if the user's active_role (session) matches one of the roles,
    OR if the user's primary role matches (fallback).
    This supports multi-role login (reviewer-as-author, convener-as-reviewer, etc.)
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            active_role = request.session.get('active_role', request.user.role)
            if active_role not in roles and request.user.role not in roles:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def _notify_conveners(subject, html_body):
    send_email_to_many(CONVENER_NOTIFY_EMAILS, subject, html_body)


def _notify_head(subject, html_body):
    send_email_via_api(HEAD_EMAIL, 'Head', subject, html_body)


# ─── AUTHOR VIEWS ───────────────────────────────────────────────

@login_required
@role_required('author', 'reviewer', 'convener')
def author_dashboard(request):
    # Only show reports submitted by this user (as author)
    reports = Report.objects.filter(author=request.user)
    reports = Report.objects.filter(author=request.user)
    stats = {
        'total': reports.count(),
        'submitted': reports.filter(status='submitted').count(),
        'under_review': reports.filter(status='under_review').count(),
        'accepted': reports.filter(status='accepted').count(),
        'revision': reports.filter(status='revision_required').count(),
        'resubmitted': reports.filter(status='resubmitted').count(),
        'resubmitted_accepted': reports.filter(status='accepted', resubmission_count__gt=0).count(),
        'awaiting_final': reports.filter(status='awaiting_final_report').count(),
    }
    return render(request, 'reports/author_dashboard.html', {
        'reports': reports,
        'stats': stats,
    })


@login_required
@role_required('author', 'reviewer', 'convener')
def submit_report(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        author_name = request.POST.get('author_name', '').strip()
        abstract = request.POST.get('abstract', '').strip()
        keywords = request.POST.get('keywords', '').strip()
        report_type = request.POST.get('report_type', '').strip()
        paper_doc = request.FILES.get('paper_doc')
        plagiarism_doc = request.FILES.get('plagiarism_doc')

        series_title = request.POST.get('series_title', '').strip()
        series_number = request.POST.get('series_number', '').strip()
        description = request.POST.get('description', '').strip()
        language = request.POST.get('language', 'English').strip()

        contributor_names = request.POST.getlist('contributor_name[]')
        contributor_emails_list = request.POST.getlist('contributor_email[]')
        pairs = [(n.strip(), e.strip()) for n, e in zip(contributor_names, contributor_emails_list) if n.strip()]
        contributors_str = ', '.join(n for n, e in pairs)
        contributor_emails_str = ', '.join(e for n, e in pairs)

        if not all([title, author_name, abstract, keywords, report_type, paper_doc]):
            messages.error(request, 'Please fill all required fields.')
            return render(request, 'reports/submit_report.html')

        report = Report.objects.create(
            author=request.user,
            title=title,
            author_name=author_name,
            contributors=contributors_str,
            contributor_emails=contributor_emails_str,
            abstract=abstract,
            keywords=keywords,
            report_type=report_type,
            paper_doc=paper_doc,
            plagiarism_doc=plagiarism_doc,
            series_title=series_title,
            series_number=series_number,
            description=description,
            language=language or 'English',
        )

        _notify_conveners(
            subject=f'New Report Submitted: {title}',
            html_body=f"""
<p>Dear Convener,</p>
<p>A new report has been submitted and requires your attention.</p>
<hr>
<h3>REPORT DETAILS</h3>
<table style="border-collapse:collapse;width:100%;">
  <tr><td style="padding:4px 16px 4px 0;"><strong>Title</strong></td><td>{title}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Author</strong></td><td>{author_name}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Publication Type</strong></td><td>{report_type.capitalize()}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Series Title</strong></td><td>{series_title or '—'}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Series Number</strong></td><td>{series_number or 'Assigned by Library'}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>DOI</strong></td><td>Assigned by Library</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Keywords</strong></td><td>{keywords}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Language</strong></td><td>{language or 'English'}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Description</strong></td><td>{description or '—'}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Contributors</strong></td><td>{contributors_str or '—'}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Submitted</strong></td><td>{timezone.now().strftime("%d %b %Y %H:%M")}</td></tr>
</table>
<hr>
<p><strong>Abstract:</strong></p>
<p>{abstract}</p>
<p>Please log in to the Internal Report Submission Portal to assign a reviewer.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )

        if pairs:
            contributor_email_recipients = [e for n, e in pairs if e]
            for contrib_email in contributor_email_recipients:
                send_email_via_api(
                    to_email=contrib_email,
                    to_name=contrib_email,
                    subject=f'Report Submitted: {title}',
                    html_body=f"""
<p>Dear Contributor,</p>
<p>You have been listed as a contributor on the following report submitted to the Internal Report Submission Portal.</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Title</strong></td><td>{title}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Author</strong></td><td>{author_name}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Type</strong></td><td>{report_type}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Submitted</strong></td><td>{timezone.now().strftime("%d %b %Y %H:%M")}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Contributors</strong></td><td>{contributors_str}</td></tr>
</table>
<p>The report is currently under review.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
                )

        messages.success(request, 'Report submitted successfully!')
        return redirect('author_dashboard')

    return render(request, 'reports/submit_report.html')


@login_required
@role_required('author', 'reviewer', 'convener')
def resubmit_report(request, report_id):
    report = get_object_or_404(Report, id=report_id, author=request.user)

    if report.status not in ('revision_required', 'head_sent_back', 'resubmitted'):
        messages.error(request, 'This report is not pending revision.')
        return redirect('author_dashboard')

    if request.method == 'POST':
        revision_notes = request.POST.get('revision_notes', '').strip()
        resubmitted_paper = request.FILES.get('resubmitted_paper_doc')

        if not resubmitted_paper:
            messages.error(request, 'Please upload the revised paper document.')
            return render(request, 'reports/resubmit_report.html', {'report': report})

        report.revision_notes = revision_notes
        report.resubmitted_paper_doc = resubmitted_paper
        report.resubmission_count += 1
        report.last_resubmitted_at = timezone.now()
        report.status = 'resubmitted'
        report.assigned_by_convener = None
        report.reassigned_at = None
        report.sent_back_to_author_at = None
        report.submission_deadline = None
        report.extension_requested = False
        report.extension_granted = False
        report.reminder_sent_at = None
        report.save()

        # Save resubmission history record
        ResubmissionHistory.objects.create(
            report=report,
            submission_number=report.resubmission_count,
            paper_doc=resubmitted_paper,
            revision_notes=revision_notes,
        )

        _notify_conveners(
            subject=f'Paper Resubmitted: {report.title}',
            html_body=f"""
<p>Dear Convener,</p>
<p>The author has resubmitted the revised paper for your review.</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Author</strong></td><td>{report.author_name}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Resubmission #</strong></td><td>{report.resubmission_count}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Resubmitted</strong></td><td>{timezone.now().strftime("%d %b %Y %H:%M")}</td></tr>
</table>
<p><strong>Author Notes:</strong><br>{revision_notes or 'No notes provided.'}</p>
<p>Please log in to the Internal Report Submission Portal to reassign the paper for review.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )

        if report.contributor_emails:
            contributor_email_recipients = [e.strip() for e in report.contributor_emails.split(',') if e.strip()]
            for contrib_email in contributor_email_recipients:
                send_email_via_api(
                    to_email=contrib_email,
                    to_name=contrib_email,
                    subject=f'Report Resubmitted: {report.title}',
                    html_body=f"""
<p>Dear Contributor,</p>
<p>The report you are listed as a contributor on has been resubmitted (Revision #{report.resubmission_count}).</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Author</strong></td><td>{report.author_name}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Resubmitted</strong></td><td>{timezone.now().strftime("%d %b %Y %H:%M")}</td></tr>
</table>
<p><strong>Author Notes:</strong><br>{revision_notes or 'No notes provided.'}</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
                )

        messages.success(request, 'Paper resubmitted successfully! The conveners have been notified.')
        return redirect('author_dashboard')

    return render(request, 'reports/resubmit_report.html', {'report': report})


@login_required
@role_required('author', 'reviewer', 'convener')
def request_extension(request, report_id):
    report = get_object_or_404(Report, id=report_id, author=request.user)

    if report.status not in ('revision_required', 'head_sent_back'):
        messages.error(request, 'Extensions can only be requested when a revision is pending.')
        return redirect('author_dashboard')

    if report.extension_requested and not report.extension_granted:
        messages.info(request, 'You have already submitted an extension request. Please wait for the convener to respond.')
        return redirect('author_dashboard')

    if request.method == 'POST':
        reason = request.POST.get('extension_reason', '').strip()
        issue_type = request.POST.get('issue_type', 'Need more time').strip()
        if not reason:
            messages.error(request, 'Please provide a reason for the extension request.')
            return render(request, 'reports/request_extension.html', {'report': report})

        full_reason = f"[{issue_type}] {reason}"

        report.extension_requested = True
        report.extension_request_reason = full_reason
        report.extension_requested_at = timezone.now()
        report.extension_granted = False
        report.save()

        _notify_conveners(
            subject=f'Extension / Issue Raised by Author: {report.title}',
            html_body=f"""
<p>Dear Convener,</p>
<p>The author has submitted a request regarding their resubmission deadline.</p>
<hr>
<h3>EXTENSION / ISSUE REQUEST</h3>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Author</strong></td><td>{report.author_name}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Request Type</strong></td><td>{issue_type}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Current Deadline</strong></td><td>{report.submission_deadline.strftime("%d %b %Y") if report.submission_deadline else "Not set"}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Requested At</strong></td><td>{timezone.now().strftime("%d %b %Y %H:%M")}</td></tr>
</table>
<p><strong>Reason / Details:</strong><br>{reason}</p>
<p>Please log in to the Internal Report Submission Portal to grant or deny the extension.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )

        messages.success(request, 'Request submitted successfully. The convener has been notified.')
        return redirect('author_dashboard')

    return render(request, 'reports/request_extension.html', {'report': report})


@login_required
@role_required('convener')
def grant_extension(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if not report.extension_requested:
        messages.error(request, 'No extension request found for this report.')
        return redirect('convener_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        extra_days = int(request.POST.get('extra_days', 7))
        convener_message = request.POST.get('convener_message', '').strip()

        if action == 'grant':
            old_deadline = report.submission_deadline or timezone.now()
            new_deadline = old_deadline + timedelta(days=extra_days)
            report.submission_deadline = new_deadline
            report.extension_granted = True
            report.extension_granted_at = timezone.now()
            report.extension_days = extra_days
            report.save()

            convener_msg_html = f"<p><strong>Convener Message:</strong><br>{convener_message}</p>" if convener_message else ""
            send_email_via_api(
                to_email=report.author.email,
                to_name=report.author_name,
                subject=f'Extension Granted: {report.title}',
                html_body=f"""
<p>Dear <strong>{report.author_name}</strong>,</p>
<p>Your extension request for the paper <em>"{report.title}"</em> has been <strong style="color:green;">GRANTED</strong>.</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>New Deadline</strong></td><td>{new_deadline.strftime("%d %b %Y")} (extended by {extra_days} days)</td></tr>
</table>
{convener_msg_html}
<p>Please log in to the Internal Report Submission Portal to resubmit your revised paper by the new deadline.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )
            messages.success(request, f'Extension granted. New deadline: {new_deadline.strftime("%d %b %Y")}.')

        else:
            report.extension_requested = False
            report.save()
            convener_msg_html = f"<p><strong>Reason:</strong><br>{convener_message}</p>" if convener_message else ""
            send_email_via_api(
                to_email=report.author.email,
                to_name=report.author_name,
                subject=f'Extension Request Denied: {report.title}',
                html_body=f"""
<p>Dear <strong>{report.author_name}</strong>,</p>
<p>Your extension request for the paper <em>"{report.title}"</em> has been <strong style="color:red;">DENIED</strong>.</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Current Deadline</strong></td><td>{report.submission_deadline.strftime("%d %b %Y") if report.submission_deadline else "Please check with convener"}</td></tr>
</table>
{convener_msg_html}
<p>Please ensure you resubmit by the original deadline. If you have urgent issues, contact your convener directly.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )
            messages.info(request, 'Extension request denied. Author has been notified.')

        return redirect('convener_dashboard')

    return render(request, 'reports/grant_extension.html', {'report': report})


@login_required
@role_required('convener')
def send_resubmission_reminder(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if report.status not in ('revision_required', 'head_sent_back'):
        messages.error(request, 'Reminders can only be sent for reports pending revision.')
        return redirect('convener_dashboard')

    now = timezone.now()
    is_overdue = report.submission_deadline and report.submission_deadline < now
    deadline_str = report.submission_deadline.strftime("%d %b %Y") if report.submission_deadline else "the stipulated timeline"

    if is_overdue:
        subject = f'OVERDUE: Resubmission Required — {report.title}'
        overdue_html = f"""
<p style="color:red;"><strong>⚠️ YOUR RESUBMISSION IS OVERDUE</strong></p>
<p>Your revised paper was due by <strong>{deadline_str}</strong>. Please resubmit immediately.</p>
<p>If you are unable to resubmit or need more time, please log in to your Author Dashboard and request an extension.</p>
"""
    else:
        subject = f'Reminder: Resubmission Deadline Approaching — {report.title}'
        overdue_html = ''

    send_email_via_api(
        to_email=report.author.email,
        to_name=report.author_name,
        subject=subject,
        html_body=f"""
<p>Dear <strong>{report.author_name}</strong>,</p>
{overdue_html}
<p>This is a reminder that your revised paper <em>"{report.title}"</em> is due for resubmission.</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Resubmission Deadline</strong></td><td>{deadline_str}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Status</strong></td><td>{"OVERDUE" if is_overdue else "Pending Resubmission"}</td></tr>
</table>
<p>If you have not yet resubmitted, please log in to the Internal Report Submission Portal to do so.</p>
<p>If you are facing any issues or need more time, you can request an extension from your Author Dashboard.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
    )

    report.reminder_sent_at = timezone.now()
    report.save()

    if is_overdue:
        messages.warning(request, f'Overdue reminder sent to {report.author.email}.')
    else:
        messages.success(request, f'Reminder sent to {report.author.email}.')
    return redirect('convener_dashboard')


@login_required
@role_required('author', 'reviewer', 'convener')
def submit_final_report(request, report_id):
    report = get_object_or_404(Report, id=report_id, author=request.user)

    if report.status != 'awaiting_final_report':
        messages.error(request, 'This report is not awaiting a final submission.')
        return redirect('author_dashboard')

    if request.method == 'POST':
        final_report_doc = request.FILES.get('final_report_doc')
        final_report_notes = request.POST.get('final_report_notes', '').strip()

        if not final_report_doc:
            messages.error(request, 'Please upload the final report document.')
            return render(request, 'reports/submit_final_report.html', {'report': report})

        report.final_report_doc = final_report_doc
        report.final_report_notes = final_report_notes
        report.final_report_submitted_at = timezone.now()
        report.status = 'final_report_submitted'
        report.save()

        _notify_conveners(
            subject=f'Final Report Submitted by Author: {report.title}',
            html_body=f"""
<p>Dear Convener,</p>
<p>The author has submitted the final report for the following paper. Please review and send it to the Head for approval.</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Author</strong></td><td>{report.author_name}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Type</strong></td><td>{report.get_report_type_display()}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Submitted</strong></td><td>{timezone.now().strftime("%d %b %Y %H:%M")}</td></tr>
</table>
<p><strong>Author Notes:</strong><br>{final_report_notes or 'No notes provided.'}</p>
<p>Please log in to the Internal Report Submission Portal to send this to the Head.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )

        messages.success(request, 'Final report submitted successfully! The convener has been notified.')
        return redirect('author_dashboard')

    return render(request, 'reports/submit_final_report.html', {'report': report})


@login_required
@role_required('author', 'reviewer', 'convener')
def report_detail_author(request, report_id):
    report = get_object_or_404(Report, id=report_id, author=request.user)
    resubmission_history = report.resubmission_history.all()
    from reports.models import ReviewerAttachmentHistory
    reviewer_attachments_all = ReviewerAttachmentHistory.objects.filter(report=report).order_by('submitted_at')
    return render(request, 'reports/report_detail_author.html', {
        'report': report,
        'resubmission_history': resubmission_history,
        'reviewer_attachments_all': reviewer_attachments_all,
    })


# ─── CONVENER VIEWS ─────────────────────────────────────────────

@login_required
@role_required('convener')
def convener_dashboard(request):
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    show_dismissed = (status_filter == 'dismissed')

    # Base queryset — exclude reports this convener dismissed (unless showing dismissed tab)
    if show_dismissed:
        reports = Report.objects.filter(dismissed_by_convener=request.user)
    else:
        reports = Report.objects.exclude(dismissed_by_convener=request.user)

    if not show_dismissed:
        if status_filter == 'resubmitted_ever':
            reports = reports.filter(resubmission_count__gt=0)
        elif status_filter == 'pending_decision':
            reports = reports.filter(status__in=['pending_convener_accept', 'pending_convener_reject'])
        elif status_filter:
            reports = reports.filter(status=status_filter)
    if type_filter:
        reports = reports.filter(report_type=type_filter)

    all_reports = Report.objects.exclude(dismissed_by_convener=request.user)
    all_reports_global = Report.objects.all()
    now = timezone.now()
    overdue_reports = all_reports.filter(
        status__in=['revision_required', 'head_sent_back'],
        submission_deadline__lt=now,
        submission_deadline__isnull=False,
    )
    reviewer_overdue_reports = all_reports.filter(
        status='under_review',
        reviewer_deadline__lt=now,
        reviewer_deadline__isnull=False,
    )
    extension_pending_reports = all_reports.filter(
        extension_requested=True,
        extension_granted=False,
    )
    stats = {
        'total': all_reports.count(),
        'submitted': all_reports.filter(status='submitted').count(),
        'under_review': all_reports.filter(status='under_review').count(),
        'accepted': all_reports.filter(status='accepted').count(),
        'revision': all_reports.filter(status='revision_required').count(),
        'resubmitted': all_reports.filter(status='resubmitted').count(),
        'rejected': all_reports.filter(status='rejected').count(),
        'pending_decision': all_reports.filter(status__in=['pending_convener_accept', 'pending_convener_reject']).count(),
        'resubmitted_ever': all_reports.filter(resubmission_count__gt=0).count(),
        'head_sent_back': all_reports.filter(status='head_sent_back').count(),
        'pending_head_approval': all_reports.filter(status='pending_head_approval').count(),
        'awaiting_final_report': all_reports.filter(status='awaiting_final_report').count(),
        'final_report_submitted': all_reports.filter(status='final_report_submitted').count(),
        'overdue_count': overdue_reports.count(),
        'reviewer_overdue_count': reviewer_overdue_reports.count(),
        'extension_pending_count': extension_pending_reports.count(),
        'dismissed_count': all_reports_global.filter(dismissed_by_convener=request.user).count(),
    }
    reviewers = User.objects.filter(role='reviewer')

    # Build a map of author_id -> count of total reports for that author
    from django.db.models import Count
    author_counts = (
        Report.objects.exclude(dismissed_by_convener=request.user)
        .values('author_id')
        .annotate(cnt=Count('id'))
        .filter(cnt__gt=1)
    )
    multi_report_authors = {row['author_id']: row['cnt'] for row in author_counts}

    return render(request, 'reports/convener_dashboard.html', {
        'reports': reports,
        'reviewers': reviewers,
        'stats': stats,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'current_convener': request.user,
        'now': now,
        'multi_report_authors': multi_report_authors,
        'show_dismissed': show_dismissed,
    })


@login_required
@role_required('convener')
def assign_reviewer(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    already_assigned_by_other = (
        report.assigned_by_convener is not None and
        report.assigned_by_convener != request.user and
        report.status == 'under_review'
    )

    if request.method == 'POST':
        if already_assigned_by_other:
            messages.error(request, 'This report has already been assigned by another convener.')
            return redirect('convener_dashboard')

        reviewer_id = request.POST.get('reviewer_id')
        reviewer = get_object_or_404(User, id=reviewer_id)

        # Block self-assignment for Niranjan and Indrani
        if (request.user.email in CONVENER_NO_SELF_ASSIGN and
                reviewer.email == request.user.email):
            messages.error(request, 'You cannot assign a report to yourself.')
            return redirect('convener_dashboard')

        report.assigned_reviewer = reviewer
        report.assigned_by_convener = request.user
        report.status = 'under_review'
        report.reassigned_at = timezone.now()
        report.reviewer_deadline = timezone.now() + timedelta(weeks=3)
        convener_notes = request.POST.get('convener_notes', '').strip()
        if convener_notes:
            report.convener_notes = convener_notes
        if report.resubmission_count > 0:
            report.reviewer_feedback = ''
            report.reviewed_at = None
            report.reviewer_attachment = None
        report.save()

        reviewer_deadline_str = report.reviewer_deadline.strftime("%d %b %Y")
        resubmission_badge = f"<p><strong>[RESUBMISSION #{report.resubmission_count}]</strong></p>" if report.resubmission_count > 0 else ""

        send_email_via_api(
            to_email=reviewer.email,
            to_name=reviewer.full_name or reviewer.email,
            subject=f'Review Assigned: {report.title}',
            html_body=f"""
<p>Dear <strong>{reviewer.full_name or reviewer.email}</strong>,</p>
<p>You have been assigned to review the following paper.</p>
{resubmission_badge}
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Author</strong></td><td>{report.author_name}</td></tr>
</table>
<h3>REVIEWER GUIDELINES</h3>
<p>The review of each report should be completed within <strong>THREE WEEKS</strong> of assignment
(deadline: <strong>{reviewer_deadline_str}</strong>). You are requested to provide critical, constructive,
and thorough reviews within the stipulated timeline.</p>
<h3>LOGIN INSTRUCTIONS</h3>
<p>You can log in to your Reviewer Dashboard at the Internal Report Submission Portal using:</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Email</strong></td><td>{reviewer.email}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Password</strong></td><td>NCMRWF@2024 (default password)</td></tr>
</table>
<p style="color:red;"><strong>IMPORTANT:</strong> After logging in, you must change your password immediately.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )

        messages.success(request, f'Reviewer assigned to "{report.title}"!')
        return redirect('convener_dashboard')

    # Include conveners who also have reviewer access (e.g. Niranjan, Indrani)
    from django.db.models import Q
    reviewers = User.objects.filter(
        Q(role='reviewer') | Q(role='convener', extra_roles__contains='reviewer')
    ).filter(is_active=True)
    return render(request, 'reports/assign_reviewer.html', {
        'report': report,
        'reviewers': reviewers,
        'already_assigned_by_other': already_assigned_by_other,
        'current_convener_email': request.user.email,
    })


@login_required
@role_required('convener')
def send_back_to_author(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if report.status not in ('revision_required', 'head_sent_back'):
        messages.error(request, 'This paper cannot be sent back to the author at this stage.')
        return redirect('convener_dashboard')

    if report.sent_back_to_author_at:
        messages.info(request, 'This paper has already been sent back to the author.')
        return redirect('convener_dashboard')

    if request.method == 'POST':
        convener_message = request.POST.get('convener_message', '').strip()
        revision_type = request.POST.get('revision_type', 'major')

        deadline_weeks = 2 if revision_type == 'minor' else 4
        deadline = timezone.now() + timedelta(weeks=deadline_weeks)

        head_notes_html = f"<p><strong>HEAD NOTES:</strong><br>{report.head_notes}</p><hr>" if report.head_notes else ""
        convener_msg_html = f"<p><strong>CONVENER MESSAGE:</strong><br>{convener_message}</p><hr>" if convener_message else ""

        send_email_via_api(
            to_email=report.author.email,
            to_name=report.author_name,
            subject=f'Action Required — Please Revise and Resubmit: {report.title}',
            html_body=f"""
<p>Dear <strong>{report.author_name}</strong>,</p>
<p>Your paper <em>"{report.title}"</em> has been reviewed and requires revisions before it can be accepted.</p>
<hr>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Revision Type</strong></td><td>{"Minor Revision" if revision_type == "minor" else "Major Revision"}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Resubmit By</strong></td><td>{deadline.strftime("%d %b %Y")} ({"2 weeks" if revision_type == "minor" else "4 weeks"} from today)</td></tr>
</table>
<hr>
<p><strong>REVIEWER FEEDBACK:</strong><br>{report.reviewer_feedback or 'Please contact your convener for detailed feedback.'}</p>
<hr>
{head_notes_html}
{convener_msg_html}
<p>Please log in to the Internal Report Submission Portal to revise and resubmit your paper.</p>
<p>If you are unable to resubmit within the deadline or are facing issues, you may request an extension from your Author Dashboard.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )

        report.sent_back_to_author_at = timezone.now()
        report.submission_deadline = deadline
        report.extension_requested = False
        report.extension_granted = False
        report.reminder_sent_at = None
        report.save()

        messages.success(
            request,
            f'Paper sent back to {report.author.email}. Deadline set: {deadline.strftime("%d %b %Y")} ({"2" if revision_type == "minor" else "4"} weeks).'
        )
        return redirect('convener_dashboard')

    return render(request, 'reports/send_back_to_author.html', {'report': report})


@login_required
@role_required('convener')
def request_final_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if report.status != 'pending_convener_accept':
        messages.error(request, 'This action is only available after a reviewer has recommended acceptance.')
        return redirect('convener_dashboard')

    if report.final_report_requested_at:
        messages.info(request, 'Final report has already been requested from the author.')
        return redirect('convener_dashboard')

    if request.method == 'POST':
        convener_message = request.POST.get('convener_message', '').strip()

        report.status = 'awaiting_final_report'
        report.final_report_requested_at = timezone.now()
        report.save()

        convener_msg_html = f"<hr><p><strong>CONVENER MESSAGE:</strong><br>{convener_message}</p>" if convener_message else ""

        send_email_via_api(
            to_email=report.author.email,
            to_name=report.author_name,
            subject=f'Action Required — Please Submit Your Final Report: {report.title}',
            html_body=f"""
<p>Dear <strong>{report.author_name}</strong>,</p>
<p>Congratulations! Your paper <em>"{report.title}"</em> has been recommended for acceptance by the reviewer.</p>
<p>You are now requested to submit the final version of your report. Please ensure the final report follows the required format and includes all necessary details.</p>
<h3>FINAL REPORT REQUIREMENTS</h3>
<ul>
  <li>Ensure the manuscript follows the prescribed format (available on the portal)</li>
  <li>Include all author and contributor details</li>
  <li>Attach a plagiarism report (Research Reports: less than 30% | Technical Reports: less than 50%)</li>
  <li>Series Number and DOI will be assigned by the Library upon final acceptance</li>
</ul>
{convener_msg_html}
<p>Please log in to the Internal Report Submission Portal to upload your final report.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )

        messages.success(request, f'Author has been notified to submit the final report for "{report.title}".')
        return redirect('convener_dashboard')

    return render(request, 'reports/request_final_report.html', {'report': report})


@login_required
@role_required('convener')
def convener_send_final_to_head(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if report.status != 'final_report_submitted':
        messages.error(request, 'This report does not have a final submission ready to send to the Head.')
        return redirect('convener_dashboard')

    if request.method == 'POST':
        convener_notes = request.POST.get('convener_notes', '').strip()
        if convener_notes:
            report.convener_notes = convener_notes

        report.status = 'pending_head_approval'
        report.sent_to_head_at = timezone.now()
        report.save()

        convener_notes_html = f"<p><strong>Convener Notes:</strong><br>{convener_notes}</p>" if convener_notes else ""
        final_notes_html = f"<p><strong>Author's Final Notes:</strong><br>{report.final_report_notes}</p>" if report.final_report_notes else ""
        final_submitted_html = f"<tr><td style='padding:4px 16px 4px 0;'><strong>Final Report Submitted</strong></td><td>{report.final_report_submitted_at.strftime('%d %b %Y %H:%M') if report.final_report_submitted_at else '—'}</td></tr>"

        _notify_head(
            subject=f'Final Report Awaiting Your Approval: {report.title}',
            html_body=f"""
<p>Dear V.S. Prasad,</p>
<p>The author has submitted the <strong>final report</strong> for the following paper and it has been verified by the convener. This is the final version ready for your approval.</p>
<hr>
<h3>FINAL REPORT DETAILS</h3>
<table style="border-collapse:collapse;width:100%;">
  <tr><td style="padding:4px 16px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Author</strong></td><td>{report.author_name}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Type</strong></td><td>{report.get_report_type_display()}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Series Title</strong></td><td>{report.series_title or '—'}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Series Number</strong></td><td>{report.series_number or 'Assigned by Library'}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>DOI</strong></td><td>Assigned by Library</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Keywords</strong></td><td>{report.keywords}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Language</strong></td><td>{report.language or 'English'}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Description</strong></td><td>{report.description or '—'}</td></tr>
  {final_submitted_html}
</table>
<hr>
<p><strong>Abstract:</strong><br>{report.abstract}</p>
<hr>
{final_notes_html}
{convener_notes_html}
<p>Please log in to the Internal Report Submission Portal to approve or send back. The final report document is available for download in the portal.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )

        messages.success(request, f'Final report for "{report.title}" sent to Head for approval.')
        return redirect('convener_dashboard')

    return render(request, 'reports/convener_send_final_to_head.html', {'report': report})


@login_required
@role_required('convener')
def convener_confirm_decision(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if report.status not in ('pending_convener_accept', 'pending_convener_reject'):
        messages.error(request, 'This report does not require a decision confirmation.')
        return redirect('convener_dashboard')

    if request.method == 'POST':
        final_decision = request.POST.get('final_decision')

        if final_decision not in ('request_final_report', 'rejected', 'revision_required'):
            messages.error(request, 'Invalid decision.')
            return redirect('convener_dashboard')

        if final_decision == 'request_final_report':
            return redirect('request_final_report', report_id=report.id)

        elif final_decision == 'rejected':
            report.status = 'rejected'
            report.save()
            send_email_via_api(
                to_email=report.author.email,
                to_name=report.author_name,
                subject=f'Report Decision: {report.title}',
                html_body=f"""
<p>Dear <strong>{report.author_name}</strong>,</p>
<p>We regret to inform you that your report <em>"{report.title}"</em> has been <strong style="color:red;">REJECTED</strong> after review.</p>
<p><strong>Reviewer Feedback:</strong><br>{report.reviewer_feedback or 'No feedback provided.'}</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )
            messages.success(request, 'Report rejected. Author has been notified.')

        elif final_decision == 'revision_required':
            report.status = 'revision_required'
            report.save()
            send_email_via_api(
                to_email=report.author.email,
                to_name=report.author_name,
                subject=f'Revision Required: {report.title}',
                html_body=f"""
<p>Dear <strong>{report.author_name}</strong>,</p>
<p>Your report <em>"{report.title}"</em> requires revisions before it can be accepted.</p>
<p><strong>Reviewer Feedback:</strong><br>{report.reviewer_feedback or 'No feedback provided.'}</p>
<p>Please log in to revise and resubmit your paper.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )
            messages.success(request, 'Revision required. Author has been notified.')

        return redirect('convener_dashboard')

    reviewer_recommended = 'Acceptance' if report.status == 'pending_convener_accept' else 'Rejection'
    return render(request, 'reports/convener_confirm_decision.html', {
        'report': report,
        'reviewer_recommended': reviewer_recommended,
    })


@login_required
@role_required('convener')
def update_status(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in dict(Report.STATUS_CHOICES):
            report.status = new_status
            report.save()
            messages.success(request, 'Status updated!')

    return redirect('convener_dashboard')


@login_required
@role_required('convener')
def report_detail_convener(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    reviewers = User.objects.filter(role='reviewer')
    resubmission_history = report.resubmission_history.all()
    from reports.models import ReviewerAttachmentHistory
    reviewer_attachments_all = ReviewerAttachmentHistory.objects.filter(report=report).order_by('submitted_at')

    return render(request, 'reports/report_detail_convener.html', {
        'report': report,
        'reviewers': reviewers,
        'resubmission_history': resubmission_history,
        'reviewer_attachments_all': reviewer_attachments_all,
    })


# ─── HEAD VIEWS ─────────────────────────────────────────────────

@login_required
@role_required('head')
def head_dashboard(request):
    # Req 4: Head sees all reports including resubmission history
    reports = Report.objects.filter(status__in=['pending_head_approval', 'accepted', 'head_sent_back'])
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')

    if status_filter:
        reports = Report.objects.all().filter(status=status_filter)
    elif not status_filter:
        reports = Report.objects.filter(status__in=['pending_head_approval', 'accepted', 'head_sent_back'])

    if type_filter:
        reports = reports.filter(report_type=type_filter)

    stats = {
        'pending_approval': Report.objects.filter(status='pending_head_approval').count(),
        'sent_back': Report.objects.filter(status='head_sent_back').count(),
        'approved': Report.objects.filter(status='accepted').count(),
        'sent_to_library': Report.objects.filter(sent_to_library_at__isnull=False).count(),
    }

    return render(request, 'reports/head_dashboard.html', {
        'reports': reports,
        'stats': stats,
        'status_filter': status_filter,
        'type_filter': type_filter,
    })


@login_required
@role_required('head')
def head_review_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    resubmission_history = report.resubmission_history.all()

    if report.status != 'pending_head_approval':
        messages.error(request, 'This report is not pending your approval.')
        return redirect('head_dashboard')

    if request.method == 'POST':
        decision = request.POST.get('decision')
        head_notes = request.POST.get('head_notes', '').strip()

        if decision == 'approve':
            report.status = 'accepted'
            report.head_notes = head_notes
            report.head_decision_at = timezone.now()
            report.save()

            send_email_via_api(
                to_email=report.author.email,
                to_name=report.author_name,
                subject=f'Congratulations! Your Report Has Been Accepted: {report.title}',
                html_body=f"""
<p>Dear <strong>{report.author_name}</strong>,</p>
<p>Great news! Your report <em>"{report.title}"</em> has been officially <strong style="color:green;">ACCEPTED</strong> by the Head.</p>
<p><strong>Reviewer Feedback:</strong><br>{report.reviewer_feedback or 'No feedback provided.'}</p>
<p>Your report will now be forwarded to the library repository.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )

            _notify_conveners(
                subject=f'Head Approved — Please Send to Librarian: {report.title}',
                html_body=f"""
<p>Dear Convener,</p>
<p>The Head (V.S. Prasad) has approved the following final report. Please send it to the librarian.</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Author</strong></td><td>{report.author_name}</td></tr>
</table>
<p><strong>Head Notes:</strong><br>{head_notes or 'No notes.'}</p>
<p>Please log in to the portal to send the paper to the librarian.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )

            messages.success(request, 'Paper approved. Author and conveners have been notified.')

        elif decision == 'send_back':
            if not head_notes:
                messages.error(request, 'Please provide notes explaining what changes are needed.')
                return render(request, 'reports/head_review_report.html', {
        'report': report,
        'resubmission_history': resubmission_history,
    })

            report.status = 'head_sent_back'
            report.head_notes = head_notes
            report.head_decision_at = timezone.now()
            report.sent_back_to_author_at = None
            report.save()

            _notify_conveners(
                subject=f'Head Sent Back Paper — Changes Needed: {report.title}',
                html_body=f"""
<p>Dear Convener,</p>
<p>The Head (V.S. Prasad) has sent back the following paper requesting changes.</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Author</strong></td><td>{report.author_name}</td></tr>
</table>
<p><strong>Head Notes (Changes Required):</strong><br>{head_notes}</p>
<p>Please log in and send this paper back to the author for revision.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )

            messages.success(request, 'Paper sent back to convener with your notes.')

        return redirect('head_dashboard')

    return render(request, 'reports/head_review_report.html', {'report': report})


@login_required
@role_required('head')
def head_send_to_library(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if report.status != 'accepted':
        messages.error(request, 'Only approved papers can be sent to the library.')
        return redirect('head_dashboard')

    if report.sent_to_library_at:
        messages.info(request, 'This paper has already been sent to the library.')
        return redirect('head_dashboard')

    if request.method == 'POST':
        head_message = request.POST.get('head_message', '').strip()
        head_msg_html = f"<p><strong>HEAD NOTE:</strong><br>{head_message}</p><hr>" if head_message else ""

        librarians = User.objects.filter(role='librarian')
        for librarian in librarians:
            send_email_via_api(
                to_email=librarian.email,
                to_name=librarian.full_name or librarian.email,
                subject=f'New Accepted Report Added to Repository: {report.title}',
                html_body=f"""
<p>Dear Librarian,</p>
<p>A new report has been approved by the Head (V.S. Prasad) and forwarded to your repository. Please assign the DOI and Series Number.</p>
<hr>
<h3>PUBLICATION DETAILS (DOI Template)</h3>
<table style="border-collapse:collapse;width:100%;">
  <tr><td style="padding:4px 16px 4px 0;"><strong>Publication Type</strong></td><td>{report.get_report_type_display()}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Series Title</strong></td><td>{report.series_title or '—'}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Series Number</strong></td><td>To be assigned by Library</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>DOI</strong></td><td>To be assigned by Library</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Keywords</strong></td><td>{report.keywords}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Year Published</strong></td><td>{report.submitted_at.strftime("%Y")}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Language</strong></td><td>{report.language or 'English'}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Publisher</strong></td><td>NCMRWF</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Description</strong></td><td>{report.description or '—'}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Author</strong></td><td>{report.author_name}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Contributors</strong></td><td>{report.contributors or '—'}</td></tr>
  <tr><td style="padding:4px 16px 4px 0;"><strong>Submitted</strong></td><td>{report.submitted_at.strftime("%d %b %Y")}</td></tr>
</table>
<hr>
{head_msg_html}
<p>Please log in to the Internal Report Submission Portal to assign the DOI and manage this publication.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )

        send_email_via_api(
            to_email=report.author.email,
            to_name=report.author_name,
            subject=f'Your Report Has Been Added to the Repository: {report.title}',
            html_body=f"""
<p>Dear <strong>{report.author_name}</strong>,</p>
<p>Congratulations! Your accepted report has been officially added to the NCMRWF publication repository.</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
</table>
<p>The DOI and Series Number will be assigned by the library team and communicated to you.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )

        report.sent_to_library_at = timezone.now()
        report.save()

        messages.success(request, f'Report "{report.title}" has been sent to the Library.')
        return redirect('head_dashboard')

    return render(request, 'reports/head_send_to_library.html', {'report': report})


# ─── REVIEWER VIEWS ─────────────────────────────────────────────

@login_required
@role_required('reviewer', 'convener')
def reviewer_dashboard(request):
    reports = Report.objects.filter(assigned_reviewer=request.user)
    from reports.models import ReviewerAttachmentHistory
    # Attach resubmission history and attachment history to each report for template use
    reports_with_history = []
    for report in reports:
        reports_with_history.append({
            'report': report,
            'resubmission_history': report.resubmission_history.all(),
            'reviewer_attachments_all': ReviewerAttachmentHistory.objects.filter(report=report).order_by('submitted_at'),
        })
    return render(request, 'reports/reviewer_dashboard.html', {
        'reports': reports,
        'reports_with_history': reports_with_history,
    })


@login_required
@role_required('reviewer', 'convener')
def submit_review(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        decision = request.POST.get('decision')
        reviewer_attachment = request.FILES.get('reviewer_attachment')

        report.reviewer_feedback = feedback
        report.reviewed_at = timezone.now()
        if reviewer_attachment:
            # CHANGE 1: Store attachment in history (never replace, always append)
            report.reviewer_attachment = reviewer_attachment
            from reports.models import ReviewerAttachmentHistory
            ReviewerAttachmentHistory.objects.create(
                report=report,
                attachment=reviewer_attachment,
                feedback_summary=feedback or '',
                resubmission_number=report.resubmission_count,
                reviewer=request.user,
            )

        # Req 3: Save feedback into ResubmissionHistory record
        if report.resubmission_count > 0:
            latest_history = report.resubmission_history.filter(
                submission_number=report.resubmission_count
            ).first()
            if latest_history:
                latest_history.reviewer_feedback = feedback
                latest_history.reviewed_at = timezone.now()
                latest_history.reviewer_decision = decision
                if reviewer_attachment:
                    latest_history.reviewer_attachment = reviewer_attachment
                latest_history.save()

        if decision == 'accepted':
            report.status = 'pending_convener_accept'
            # Req 2: Also notify author about reviewer acceptance
            send_email_via_api(
                to_email=report.author.email,
                to_name=report.author_name,
                subject=f'Update on Your Report: {report.title}',
                html_body=f"""
<p>Dear <strong>{report.author_name}</strong>,</p>
<p>Your report <em>"{report.title}"</em> has been reviewed. The reviewer has recommended <strong style="color:green;">ACCEPTANCE</strong>.</p>
<p>The convener will now review this recommendation and may contact you regarding a final report submission.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )
            _notify_conveners(
                subject=f'Reviewer Recommends ACCEPTANCE — Action Needed: {report.title}',
                html_body=f"""
<p>Dear Convener,</p>
<p>The reviewer has recommended <strong style="color:green;">ACCEPTANCE</strong> for the following report.
Please log in to request the final report from the author or override this decision.</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Author</strong></td><td>{report.author_name}</td></tr>
</table>
<p><strong>Reviewer Feedback:</strong><br>{feedback}</p>
<p>Action required: Please request the final report from the author, or override to revision/rejection.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )

        elif decision == 'revision_required':
            report.status = 'revision_required'
            # Req 2: Notify author of reviewer feedback
            send_email_via_api(
                to_email=report.author.email,
                to_name=report.author_name,
                subject=f'Reviewer Feedback on Your Report: {report.title}',
                html_body=f"""
<p>Dear <strong>{report.author_name}</strong>,</p>
<p>The reviewer has reviewed your report <em>"{report.title}"</em> and has requested revisions.</p>
<p><strong>Reviewer Feedback:</strong><br>{feedback or 'No feedback provided.'}</p>
<p>The convener will contact you with detailed instructions for revision and resubmission.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )
            _notify_conveners(
                subject=f'Revision Required — Author Notified: {report.title}',
                html_body=f"""
<p>Dear Convener,</p>
<p>The reviewer has requested revisions for:</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Author</strong></td><td>{report.author_name}</td></tr>
</table>
<p><strong>Reviewer Feedback:</strong><br>{feedback}</p>
<p>Please log in and use "Send Back to Author" once you are ready.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )

        elif decision == 'rejected':
            report.status = 'pending_convener_reject'
            # Req 2: Notify author of reviewer recommendation
            send_email_via_api(
                to_email=report.author.email,
                to_name=report.author_name,
                subject=f'Update on Your Report: {report.title}',
                html_body=f"""
<p>Dear <strong>{report.author_name}</strong>,</p>
<p>The reviewer has submitted their assessment for your report <em>"{report.title}"</em>.</p>
<p><strong>Reviewer Feedback:</strong><br>{feedback or 'No feedback provided.'}</p>
<p>The convener will review the recommendation and notify you of the final decision.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )
            _notify_conveners(
                subject=f'Reviewer Recommends REJECTION — Confirm Needed: {report.title}',
                html_body=f"""
<p>Dear Convener,</p>
<p>The reviewer has recommended <strong style="color:red;">REJECTION</strong> for the following report.
Please log in to confirm or override this decision.</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Author</strong></td><td>{report.author_name}</td></tr>
</table>
<p><strong>Reviewer Feedback:</strong><br>{feedback}</p>
<p>Action required: Please confirm rejection or override to revision/acceptance.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
            )

        report.save()
        messages.success(request, 'Review submitted! The conveners have been notified.')
        return redirect('reviewer_dashboard')

    return render(request, 'reports/submit_review.html', {'report': report})


# ─── LIBRARIAN VIEWS ────────────────────────────────────────────

@login_required
@role_required('librarian')
def librarian_dashboard(request):
    reports = Report.objects.filter(status='accepted', sent_to_library_at__isnull=False)
    type_filter = request.GET.get('type', '')
    if type_filter:
        reports = reports.filter(report_type=type_filter)

    stats = {
        'total_accepted': reports.count(),
        'technical': reports.filter(report_type='technical').count(),
        'verification': reports.filter(report_type='verification').count(),
        'research': reports.filter(report_type='research').count(),
        'doi_pending': reports.filter(doi='').count(),
    }
    return render(request, 'reports/librarian_dashboard.html', {
        'reports': reports,
        'stats': stats,
    })


@login_required
@role_required('librarian')
def assign_doi(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if report.status != 'accepted' or not report.sent_to_library_at:
        messages.error(request, 'DOI can only be assigned to reports in the library.')
        return redirect('librarian_dashboard')

    if request.method == 'POST':
        doi = request.POST.get('doi', '').strip()
        series_number = request.POST.get('series_number', '').strip()

        if not doi:
            messages.error(request, 'Please enter a DOI.')
            return render(request, 'reports/assign_doi.html', {'report': report})

        report.doi = doi
        if series_number:
            report.series_number = series_number
        report.doi_assigned_by = request.user
        report.doi_assigned_at = timezone.now()
        report.save()

        send_email_via_api(
            to_email=report.author.email,
            to_name=report.author_name,
            subject=f'DOI Assigned to Your Report: {report.title}',
            html_body=f"""
<p>Dear <strong>{report.author_name}</strong>,</p>
<p>The library has assigned a DOI to your accepted report.</p>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Title</strong></td><td>{report.title}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>DOI</strong></td><td>{doi}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Series Number</strong></td><td>{series_number or report.series_number or '—'}</td></tr>
</table>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )

        messages.success(request, f'DOI "{doi}" assigned to "{report.title}".')
        return redirect('librarian_dashboard')

    return render(request, 'reports/assign_doi.html', {'report': report})


# ─── PDF FILENAME ENCRYPTION UTILS ────────────────────────────────────────────
import base64, hashlib, os as _os
from django.conf import settings as _settings

def _get_cipher_key():
    secret = _settings.PDF_FILENAME_SECRET.encode()
    return hashlib.sha256(secret).digest()

def encrypt_filename(filename):
    key = _get_cipher_key()
    fb = filename.encode('utf-8')
    encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(fb))
    token = base64.urlsafe_b64encode(encrypted).decode().rstrip('=')
    return token

def decrypt_filename(token):
    key = _get_cipher_key()
    padding = 4 - len(token) % 4
    if padding != 4:
        token = token + '=' * padding
    encrypted = base64.urlsafe_b64decode(token.encode())
    fb = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
    return fb.decode('utf-8')


@login_required
def serve_encrypted_pdf(request):
    import mimetypes
    from django.http import FileResponse, Http404

    token = request.GET.get('t', '')
    if not token:
        raise Http404("No file token provided.")

    try:
        relative_path = decrypt_filename(token)
    except Exception:
        raise Http404("Invalid file token.")

    abs_path = _os.path.join(_settings.MEDIA_ROOT, relative_path)
    abs_path = _os.path.normpath(abs_path)

    if not abs_path.startswith(_os.path.normpath(_settings.MEDIA_ROOT)):
        raise Http404("Access denied.")

    if not _os.path.exists(abs_path):
        raise Http404("File not found.")

    mime_type, _ = mimetypes.guess_type(abs_path)
    mime_type = mime_type or 'application/octet-stream'

    response = FileResponse(open(abs_path, 'rb'), content_type=mime_type)
    disposition = 'inline' if mime_type == 'application/pdf' else 'attachment'
    response['Content-Disposition'] = f'{disposition}; filename="document{_os.path.splitext(abs_path)[1]}"'
    return response


# ─────────────────────────────────────────────────────────────
#  SUPPORT REQUEST VIEWS
# ─────────────────────────────────────────────────────────────

@login_required
@role_required('author', 'reviewer', 'convener')
def author_support(request):
    my_requests = SupportRequest.objects.filter(author=request.user)
    my_reports = Report.objects.filter(author=request.user).exclude(
        status__in=['accepted', 'rejected']
    )

    if request.method == 'POST':
        request_type = request.POST.get('request_type', 'general')
        subject = request.POST.get('subject', '').strip()
        message_body = request.POST.get('message', '').strip()
        report_id = request.POST.get('report_id', '').strip()

        if not subject or not message_body:
            messages.error(request, 'Please fill in both subject and message.')
            return render(request, 'reports/author_support.html', {
                'my_requests': my_requests,
                'my_reports': my_reports,
            })

        linked_report = None
        if report_id:
            try:
                linked_report = Report.objects.get(id=report_id, author=request.user)
            except Report.DoesNotExist:
                pass

        sr = SupportRequest.objects.create(
            author=request.user,
            report=linked_report,
            request_type=request_type,
            subject=subject,
            message=message_body,
        )

        report_row = f"<tr><td style='padding:4px 12px 4px 0;'><strong>Linked Report</strong></td><td>{linked_report.title}</td></tr>" if linked_report else ""

        _notify_conveners(
            subject=f'[Support Request] {sr.get_request_type_display()} — {subject}',
            html_body=f"""
<p>Dear Convener,</p>
<p>An author has submitted a support request via the Author Dashboard.</p>
<hr>
<h3>SUPPORT REQUEST #{sr.id}</h3>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Author</strong></td><td>{request.user.full_name or request.user.email}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Request Type</strong></td><td>{sr.get_request_type_display()}</td></tr>
  {report_row}
  <tr><td style="padding:4px 12px 4px 0;"><strong>Subject</strong></td><td>{subject}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Submitted At</strong></td><td>{timezone.now().strftime("%d %b %Y %H:%M")}</td></tr>
</table>
<p><strong>Message:</strong><br>{message_body}</p>
<p>Please log in to the Convener Dashboard → Support Inbox to respond.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )

        messages.success(request, 'Your support request has been submitted. The convener will respond shortly.')
        return redirect('author_support')

    return render(request, 'reports/author_support.html', {
        'my_requests': my_requests,
        'my_reports': my_reports,
    })


@login_required
@role_required('convener')
def convener_delete_report(request, report_id):
    """Convener permanently deletes a report (hard delete).
    Intended for removing duplicate or invalid submissions.
    Requires POST with confirmation."""
    if request.method == 'POST':
        report = get_object_or_404(Report, id=report_id)
        report_title = report.title
        author_email = report.author.email
        report.delete()
        messages.success(
            request,
            f'Report "{report_title}" by {author_email} has been permanently deleted.'
        )
    return redirect('convener_dashboard')


@login_required
@role_required('convener')
def convener_dismiss_report(request, report_id):
    """Convener dismisses (hides) a report from their own dashboard view.
    The report is NOT deleted — it remains visible to other conveners and all other roles.
    The dismissal can be undone from the 'Dismissed' filter."""
    if request.method == 'POST':
        report = get_object_or_404(Report, id=report_id)
        report.dismissed_by_convener.add(request.user)
        messages.success(request, f'Report "{report.title}" has been dismissed from your view.')
    return redirect('convener_dashboard')


@login_required
@role_required('convener')
def convener_undismiss_report(request, report_id):
    """Restore a previously dismissed report back to the convener's dashboard."""
    if request.method == 'POST':
        report = get_object_or_404(Report, id=report_id)
        report.dismissed_by_convener.remove(request.user)
        messages.success(request, f'Report "{report.title}" has been restored to your dashboard.')
    return redirect('convener_dashboard')


@login_required
@role_required('convener')
def convener_support_inbox(request):
    status_filter = request.GET.get('status', 'open')
    all_requests = SupportRequest.objects.all()

    if status_filter == 'all':
        requests_qs = all_requests
    else:
        requests_qs = all_requests.filter(status=status_filter)

    stats = {
        'open': all_requests.filter(status='open').count(),
        'responded': all_requests.filter(status='responded').count(),
        'closed': all_requests.filter(status='closed').count(),
        'total': all_requests.count(),
    }

    return render(request, 'reports/convener_support_inbox.html', {
        'requests': requests_qs,
        'stats': stats,
        'status_filter': status_filter,
    })


@login_required
@role_required('convener')
def convener_respond_support(request, support_id):
    sr = get_object_or_404(SupportRequest, id=support_id)

    if request.method == 'POST':
        response_text = request.POST.get('response', '').strip()
        action = request.POST.get('action', 'respond')

        if not response_text:
            messages.error(request, 'Please enter a response message.')
            return render(request, 'reports/convener_respond_support.html', {'sr': sr})

        sr.convener_response = response_text
        sr.responded_at = timezone.now()
        sr.responded_by = request.user
        sr.status = 'closed' if action == 'close' else 'responded'
        sr.save()

        report_row = f"<tr><td style='padding:4px 12px 4px 0;'><strong>Linked Report</strong></td><td>{sr.report.title}</td></tr>" if sr.report else ""

        send_email_via_api(
            to_email=sr.author.email,
            to_name=sr.author.full_name or sr.author.email,
            subject=f'[Support] Response to your request: {sr.subject}',
            html_body=f"""
<p>Dear <strong>{sr.author.full_name or sr.author.email}</strong>,</p>
<p>Your support request has been reviewed and a response has been provided.</p>
<hr>
<h3>YOUR REQUEST</h3>
<table style="border-collapse:collapse;">
  <tr><td style="padding:4px 12px 4px 0;"><strong>Request Type</strong></td><td>{sr.get_request_type_display()}</td></tr>
  {report_row}
  <tr><td style="padding:4px 12px 4px 0;"><strong>Subject</strong></td><td>{sr.subject}</td></tr>
  <tr><td style="padding:4px 12px 4px 0;"><strong>Status</strong></td><td>{"Closed" if sr.status == "closed" else "Responded — awaiting your follow-up"}</td></tr>
</table>
<hr>
<p><strong>Convener's Response:</strong><br>{response_text}</p>
<p>Please log in to your Author Dashboard → Support tab to view the full thread.</p>
<br><p>— Internal Report Submission Portal Team</p>
""",
        )

        messages.success(request, f'Response sent to {sr.author.email}.')
        return redirect('convener_support_inbox')

    return render(request, 'reports/convener_respond_support.html', {'sr': sr})