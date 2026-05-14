from django.db import migrations, models


class Migration(migrations.Migration):
    """
    No schema changes needed for admin — Django's built-in is_staff
    field already exists on AbstractBaseUser and handles the admin flag.
    This migration is a placeholder confirming the admin dashboard
    uses is_staff rather than a new role.
    """
    dependencies = [
        ('accounts', '0003_add_head_role'),
    ]

    operations = [
        # Ensure the role field still covers all five roles.
        # Admin access is controlled via is_staff=True, not a role value.
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
                ],
                default='author',
                max_length=20,
            ),
        ),
    ]
