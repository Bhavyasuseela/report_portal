from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def add_fields_if_not_exist(apps, schema_editor):
    """Safely add columns only if they don't already exist (MySQL safe)."""
    from django.db import connection

    # Get existing columns
    with connection.cursor() as cursor:
        cursor.execute("SHOW COLUMNS FROM `reports_report`")
        existing = {row[0] for row in cursor.fetchall()}

    # Get the actual type of accounts_user.id so FK matches exactly
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COLUMN_TYPE FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'accounts_user' AND COLUMN_NAME = 'id'"
        )
        row = cursor.fetchone()
        user_id_type = row[0] if row else 'bigint'  # e.g. 'bigint' or 'int'

    # TEXT/longtext columns cannot have DEFAULT in MySQL — omit DEFAULT clause
    fields_to_add = [
        ('final_report_requested_at', "ALTER TABLE `reports_report` ADD COLUMN `final_report_requested_at` datetime(6) NULL"),
        ('final_report_doc',          "ALTER TABLE `reports_report` ADD COLUMN `final_report_doc` varchar(100) NOT NULL DEFAULT ''"),
        ('final_report_notes',        "ALTER TABLE `reports_report` ADD COLUMN `final_report_notes` longtext NOT NULL"),
        ('final_report_submitted_at', "ALTER TABLE `reports_report` ADD COLUMN `final_report_submitted_at` datetime(6) NULL"),
        ('series_title',              "ALTER TABLE `reports_report` ADD COLUMN `series_title` varchar(300) NOT NULL DEFAULT ''"),
        ('series_number',             "ALTER TABLE `reports_report` ADD COLUMN `series_number` varchar(100) NOT NULL DEFAULT ''"),
        ('description',               "ALTER TABLE `reports_report` ADD COLUMN `description` longtext NOT NULL"),
        ('language',                  "ALTER TABLE `reports_report` ADD COLUMN `language` varchar(50) NOT NULL DEFAULT 'English'"),
        ('doi',                       "ALTER TABLE `reports_report` ADD COLUMN `doi` varchar(200) NOT NULL DEFAULT ''"),
        ('doi_assigned_at',           "ALTER TABLE `reports_report` ADD COLUMN `doi_assigned_at` datetime(6) NULL"),
        # Use the same type as accounts_user.id to avoid FK type mismatch
        ('doi_assigned_by_id',        f"ALTER TABLE `reports_report` ADD COLUMN `doi_assigned_by_id` {user_id_type} NULL"),
    ]

    with connection.cursor() as cursor:
        for col, sql in fields_to_add:
            if col not in existing:
                try:
                    cursor.execute(sql)
                except Exception as e:
                    if '1060' in str(e) or 'Duplicate column' in str(e):
                        pass  # already exists, skip
                    else:
                        raise

        # Add FK constraint for doi_assigned_by_id (skip if already exists)
        if 'doi_assigned_by_id' not in existing:
            try:
                cursor.execute(
                    "ALTER TABLE `reports_report` ADD CONSTRAINT `reports_report_doi_assigned_by_id_fk` "
                    "FOREIGN KEY (`doi_assigned_by_id`) REFERENCES `accounts_user` (`id`) ON DELETE SET NULL"
                )
            except Exception as e:
                err = str(e)
                if '1826' in err or '1061' in err or 'Duplicate key' in err or 'already exists' in err.lower():
                    pass  # constraint already exists, skip
                else:
                    raise


def reverse_fields(apps, schema_editor):
    pass  # Don't auto-reverse to avoid data loss


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0006_head_workflow'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(add_fields_if_not_exist, reverse_fields),
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(
                choices=[
                    ('submitted', 'Submitted'),
                    ('under_review', 'Under Review'),
                    ('revision_required', 'Revision Required'),
                    ('resubmitted', 'Resubmitted'),
                    ('pending_convener_accept', 'Pending Convener Acceptance'),
                    ('pending_convener_reject', 'Pending Convener Rejection'),
                    ('awaiting_final_report', 'Awaiting Final Report from Author'),
                    ('final_report_submitted', 'Final Report Submitted'),
                    ('pending_head_approval', 'Pending Head Approval'),
                    ('head_sent_back', 'Sent Back by Head'),
                    ('accepted', 'Accepted'),
                    ('rejected', 'Rejected'),
                ],
                default='submitted',
                max_length=30,
            ),
        ),
    ]
