from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Adds 'admin' as a proper role value in ROLE_CHOICES.
    Admin access is controlled by role='admin', separate from is_staff.
    """
    dependencies = [
        ('accounts', '0004_add_admin_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('author', 'Author'),
                    ('convener', 'Convener'),
                    ('reviewer', 'Reviewer'),
                    ('librarian', 'Librarian'),
                    ('head', 'Head'),
                    ('admin', 'Admin'),
                ],
                default='author',
                max_length=20,
            ),
        ),
    ]
