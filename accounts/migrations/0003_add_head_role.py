from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_role'),
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
                ],
                default='author',
                max_length=20,
            ),
        ),
    ]
