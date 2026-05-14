from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_password_reset_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='extra_roles',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Comma-separated additional roles this user can access',
                max_length=200,
            ),
        ),
    ]
