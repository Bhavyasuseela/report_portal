from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0009_sync_doi_publication_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_type', models.CharField(
                    choices=[
                        ('time_extension', 'Request More Time to Submit'),
                        ('submission_issue', 'Issue While Submitting Report'),
                        ('document_issue', 'Document / File Issue'),
                        ('review_query', 'Query About Review Status'),
                        ('general', 'General Query'),
                        ('other', 'Other'),
                    ],
                    default='general',
                    max_length=30,
                )),
                ('subject', models.CharField(max_length=300)),
                ('message', models.TextField()),
                ('status', models.CharField(
                    choices=[('open', 'Open'), ('responded', 'Responded'), ('closed', 'Closed')],
                    default='open',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('convener_response', models.TextField(blank=True)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('report', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='support_requests',
                    to='reports.report',
                )),
                ('author', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='support_requests',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('responded_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='support_responses',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
