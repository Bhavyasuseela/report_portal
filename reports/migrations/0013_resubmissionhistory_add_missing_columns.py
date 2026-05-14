from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Migration 0012 used SeparateDatabaseAndState with empty database_operations,
    meaning the ResubmissionHistory table was created in the database without the
    reviewer_feedback, reviewer_attachment, reviewed_at, and reviewer_decision columns.
    This migration adds those missing columns to the actual database table.
    """

    dependencies = [
        ('reports', '0012_resubmission_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='resubmissionhistory',
            name='reviewer_feedback',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='resubmissionhistory',
            name='reviewer_attachment',
            field=models.FileField(blank=True, null=True, upload_to='reviewer_attachments/history/'),
        ),
        migrations.AddField(
            model_name='resubmissionhistory',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='resubmissionhistory',
            name='reviewer_decision',
            field=models.CharField(blank=True, default='', max_length=30),
            preserve_default=False,
        ),
    ]
