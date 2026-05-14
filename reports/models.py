from django.db import models
from accounts.models import User


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('technical', 'Technical Report'),
        ('verification', 'Verification Report'),
        ('research', 'Research Report'),
    ]
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('revision_required', 'Revision Required'),
        ('resubmitted', 'Resubmitted'),
        ('pending_convener_accept', 'Pending Convener Acceptance'),
        ('pending_convener_reject', 'Pending Convener Rejection'),
        # NEW: Convener asks author for final report after reviewer accepts
        ('awaiting_final_report', 'Awaiting Final Report from Author'),
        # NEW: Author submitted final report, convener must send to head
        ('final_report_submitted', 'Final Report Submitted'),
        ('pending_head_approval', 'Pending Head Approval'),
        ('head_sent_back', 'Sent Back by Head'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=300)
    author_name = models.CharField(max_length=200)
    contributors = models.TextField(blank=True, help_text='Comma-separated contributor names')
    contributor_emails = models.TextField(blank=True, help_text='Comma-separated contributor emails (same order as contributors)')
    abstract = models.TextField()
    keywords = models.CharField(max_length=500)
    plagiarism_doc = models.FileField(upload_to='plagiarism/', null=True, blank=True)
    paper_doc = models.FileField(upload_to='papers/')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    convener_notes = models.TextField(blank=True)
    assigned_reviewer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_reports'
    )
    assigned_by_convener = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='convener_assignments'
    )
    reviewer_feedback = models.TextField(blank=True)
    reviewer_attachment = models.FileField(upload_to='reviewer_attachments/', null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # Revision / resubmission tracking
    revision_notes = models.TextField(blank=True, help_text='Author notes when resubmitting after revision')
    resubmitted_paper_doc = models.FileField(upload_to='papers/resubmissions/', null=True, blank=True)
    resubmission_count = models.PositiveIntegerField(default=0)
    last_resubmitted_at = models.DateTimeField(null=True, blank=True)

    # Track send-to-author action (to disable button after sending)
    sent_back_to_author_at = models.DateTimeField(null=True, blank=True)

    # Track reassign action (to disable button after reassigning)
    reassigned_at = models.DateTimeField(null=True, blank=True)

    # Head workflow fields
    head_notes = models.TextField(blank=True, help_text='Notes from Head to convener when sending back')
    sent_to_head_at = models.DateTimeField(null=True, blank=True)
    head_decision_at = models.DateTimeField(null=True, blank=True)
    sent_to_library_at = models.DateTimeField(null=True, blank=True)

    # NEW: Final report workflow
    final_report_requested_at = models.DateTimeField(null=True, blank=True)
    final_report_doc = models.FileField(upload_to='papers/final/', null=True, blank=True)
    final_report_notes = models.TextField(blank=True)
    final_report_submitted_at = models.DateTimeField(null=True, blank=True)

    # Submission timelines
    submission_deadline = models.DateTimeField(null=True, blank=True, help_text='Deadline for author resubmission (4 weeks major / 2 weeks minor)')
    reviewer_deadline = models.DateTimeField(null=True, blank=True, help_text='Deadline for reviewer to complete review (3 weeks)')
    reminder_sent_at = models.DateTimeField(null=True, blank=True, help_text='When convener reminder was last sent to author')

    # Extension requests by author
    extension_requested = models.BooleanField(default=False)
    extension_request_reason = models.TextField(blank=True)
    extension_requested_at = models.DateTimeField(null=True, blank=True)
    extension_granted = models.BooleanField(default=False)
    extension_granted_at = models.DateTimeField(null=True, blank=True)
    extension_days = models.PositiveIntegerField(default=0)

    # NEW: DOI / Publication Metadata
    series_title = models.CharField(max_length=300, blank=True)
    series_number = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=50, blank=True, default='English')
    doi = models.CharField(max_length=200, blank=True)
    doi_assigned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='doi_assignments'
    )
    doi_assigned_at = models.DateTimeField(null=True, blank=True)

    # Conveners who have dismissed this report from their view
    dismissed_by_convener = models.ManyToManyField(
        User, blank=True, related_name='dismissed_reports',
        help_text='Conveners who have dismissed this report from their dashboard view.'
    )

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.title} by {self.author_name} [{self.get_status_display()}]"

    def get_status_color(self):
        colors = {
            'submitted': 'blue',
            'under_review': 'amber',
            'revision_required': 'coral',
            'resubmitted': 'purple',
            'pending_convener_accept': 'teal',
            'pending_convener_reject': 'orange',
            'awaiting_final_report': 'indigo',
            'final_report_submitted': 'teal',
            'pending_head_approval': 'indigo',
            'head_sent_back': 'coral',
            'accepted': 'green',
            'rejected': 'red',
        }
        return colors.get(self.status, 'gray')

    def get_active_paper_doc(self):
        """Returns the most recent paper document (final > resubmitted > original)."""
        if self.final_report_doc:
            return self.final_report_doc
        return self.resubmitted_paper_doc if self.resubmitted_paper_doc else self.paper_doc


class SupportRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('time_extension', 'Request More Time to Submit'),
        ('submission_issue', 'Issue While Submitting Report'),
        ('document_issue', 'Document / File Issue'),
        ('review_query', 'Query About Review Status'),
        ('general', 'General Query'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('responded', 'Responded'),
        ('closed', 'Closed'),
    ]

    report = models.ForeignKey(
        'Report', on_delete=models.CASCADE, related_name='support_requests',
        null=True, blank=True,
        help_text='Leave blank if not related to a specific report'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_requests')
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPE_CHOICES, default='general')
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    convener_response = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='support_responses'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_request_type_display()}] {self.subject} — {self.author.email}"


class ReviewerAttachmentHistory(models.Model):
    """Stores ALL reviewer attachments across reviews — never replaces, always appends."""
    report = models.ForeignKey('Report', on_delete=models.CASCADE, related_name='reviewer_attachments_history')
    attachment = models.FileField(upload_to='reviewer_attachments/history/')
    feedback_summary = models.TextField(blank=True, help_text='Reviewer feedback text at time of upload')
    submitted_at = models.DateTimeField(auto_now_add=True)
    resubmission_number = models.PositiveIntegerField(default=0, help_text='0 = original submission review')
    reviewer = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='submitted_attachments'
    )

    class Meta:
        ordering = ['submitted_at']

    def __str__(self):
        return f"Attachment for {self.report.title} — review #{self.resubmission_number} at {self.submitted_at:%d %b %Y}"


class ResubmissionHistory(models.Model):
    """Tracks each individual resubmission with its documents and feedback."""
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='resubmission_history')
    submission_number = models.PositiveIntegerField()  # 1, 2, 3...
    submitted_at = models.DateTimeField(auto_now_add=True)
    paper_doc = models.FileField(upload_to='papers/resubmissions/')
    revision_notes = models.TextField(blank=True)

    # Reviewer feedback for THIS resubmission (copied when reviewer reviews)
    reviewer_feedback = models.TextField(blank=True)
    reviewer_attachment = models.FileField(upload_to='reviewer_attachments/history/', null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer_decision = models.CharField(max_length=30, blank=True)  # accepted/revision_required/rejected

    class Meta:
        ordering = ['submission_number']

    def __str__(self):
        return f"{self.report.title} — Resubmission #{self.submission_number}"
