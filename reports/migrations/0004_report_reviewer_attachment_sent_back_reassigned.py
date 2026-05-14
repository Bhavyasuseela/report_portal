from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_report_assigned_by_convener'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='reviewer_attachment',
            field=models.FileField(blank=True, null=True, upload_to='reviewer_attachments/'),
        ),
        migrations.AddField(
            model_name='report',
            name='sent_back_to_author_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='reassigned_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
