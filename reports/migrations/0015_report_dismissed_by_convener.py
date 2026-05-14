from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0014_reviewer_attachment_history'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='dismissed_by_convener',
            field=models.ManyToManyField(
                blank=True,
                help_text='Conveners who have dismissed this report from their dashboard view.',
                related_name='dismissed_reports',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
