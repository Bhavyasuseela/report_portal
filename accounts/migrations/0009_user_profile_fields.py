from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_user_extra_roles'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='designation',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='user',
            name='department',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='user',
            name='is_approved',
            field=models.BooleanField(
                default=False,
                help_text='For self-registered authors: must be approved by admin before they can log in.',
            ),
        ),
    ]
