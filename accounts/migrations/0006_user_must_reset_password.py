from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_add_admin_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='must_reset_password',
            field=models.BooleanField(default=True),
        ),
    ]
