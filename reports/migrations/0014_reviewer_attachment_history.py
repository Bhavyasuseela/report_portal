from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_user_extra_roles'),
        ('reports', '0013_resubmissionhistory_add_missing_columns'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewerAttachmentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment', models.FileField(upload_to='reviewer_attachments/history/')),
                ('feedback_summary', models.TextField(blank=True, help_text='Reviewer feedback text at time of upload')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('resubmission_number', models.PositiveIntegerField(default=0, help_text='0 = original submission review')),
                ('report', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reviewer_attachments_history',
                    to='reports.report',
                )),
                ('reviewer', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='submitted_attachments',
                    to='accounts.user',
                )),
            ],
            options={
                'ordering': ['submitted_at'],
            },
        ),
    ]
