from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_report_reviewer_attachment_sent_back_reassigned'),
    ]

    operations = [
        # Store contributor emails alongside names
        migrations.AddField(
            model_name='report',
            name='contributor_emails',
            field=models.TextField(
                blank=True,
                help_text='Comma-separated contributor emails (same order as contributors field)',
            ),
        ),
        # Reviewer recommendation: pending_convener_accept / pending_convener_reject
        # These are intermediate statuses before convener makes the final call
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(
                max_length=30,
                choices=[
                    ('submitted', 'Submitted'),
                    ('under_review', 'Under Review'),
                    ('revision_required', 'Revision Required'),
                    ('resubmitted', 'Resubmitted'),
                    ('pending_convener_accept', 'Pending Convener Acceptance'),
                    ('pending_convener_reject', 'Pending Convener Rejection'),
                    ('accepted', 'Accepted'),
                    ('rejected', 'Rejected'),
                ],
                default='submitted',
            ),
        ),
    ]
