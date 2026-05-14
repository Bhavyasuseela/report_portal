from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='revision_notes',
            field=models.TextField(blank=True, help_text='Author notes when resubmitting after revision'),
        ),
        migrations.AddField(
            model_name='report',
            name='resubmitted_paper_doc',
            field=models.FileField(blank=True, null=True, upload_to='papers/resubmissions/'),
        ),
        migrations.AddField(
            model_name='report',
            name='resubmission_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='report',
            name='last_resubmitted_at',
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
                    ('accepted', 'Accepted'),
                    ('rejected', 'Rejected'),
                ],
                default='submitted',
                max_length=30,
            ),
        ),
    ]
