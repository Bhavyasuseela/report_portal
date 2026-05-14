from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_contributor_emails_reviewer_decision'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='head_notes',
            field=models.TextField(blank=True, help_text='Notes from Head to convener when sending back'),
        ),
        migrations.AddField(
            model_name='report',
            name='sent_to_head_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='head_decision_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='sent_to_library_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(
                choices=[
                    ('submitted', 'Submitted'),
                    ('under_review', 'Under Review'),
                    ('revision_required', 'Revision Required'),
                    ('resubmitted', 'Resubmitted'),
                    ('pending_convener_accept', 'Pending Convener Acceptance'),
                    ('pending_convener_reject', 'Pending Convener Rejection'),
                    ('pending_head_approval', 'Pending Head Approval'),
                    ('head_sent_back', 'Sent Back by Head'),
                    ('accepted', 'Accepted'),
                    ('rejected', 'Rejected'),
                ],
                default='submitted',
                max_length=30,
            ),
        ),
    ]
