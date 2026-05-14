from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0011_alter_report_contributor_emails_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Database: do nothing — table already exists
            database_operations=[],
            # State: tell Django the model exists
            state_operations=[
                migrations.CreateModel(
                    name='ResubmissionHistory',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('submission_number', models.PositiveIntegerField()),
                        ('submitted_at', models.DateTimeField(auto_now_add=True)),
                        ('paper_doc', models.FileField(upload_to='papers/resubmissions/')),
                        ('revision_notes', models.TextField(blank=True)),
                        ('reviewer_feedback', models.TextField(blank=True)),
                        ('reviewer_attachment', models.FileField(blank=True, null=True, upload_to='reviewer_attachments/history/')),
                        ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                        ('reviewer_decision', models.CharField(blank=True, max_length=30)),
                        ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resubmission_history', to='reports.report')),
                    ],
                    options={
                        'ordering': ['submission_number'],
                    },
                ),
            ],
        ),
    ]
