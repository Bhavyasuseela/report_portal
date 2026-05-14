from django.db import migrations, models


def add_timeline_fields(apps, schema_editor):
    """Safely add new columns for timelines and extensions (skips existing columns)."""
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SHOW COLUMNS FROM `reports_report`")
        existing = {row[0] for row in cursor.fetchall()}

    fields_to_add = [
        ('submission_deadline',      "ALTER TABLE `reports_report` ADD COLUMN `submission_deadline` datetime(6) NULL"),
        ('reviewer_deadline',        "ALTER TABLE `reports_report` ADD COLUMN `reviewer_deadline` datetime(6) NULL"),
        ('reminder_sent_at',         "ALTER TABLE `reports_report` ADD COLUMN `reminder_sent_at` datetime(6) NULL"),
        ('extension_requested',      "ALTER TABLE `reports_report` ADD COLUMN `extension_requested` tinyint(1) NOT NULL DEFAULT 0"),
        ('extension_request_reason', "ALTER TABLE `reports_report` ADD COLUMN `extension_request_reason` longtext NOT NULL"),
        ('extension_requested_at',   "ALTER TABLE `reports_report` ADD COLUMN `extension_requested_at` datetime(6) NULL"),
        ('extension_granted',        "ALTER TABLE `reports_report` ADD COLUMN `extension_granted` tinyint(1) NOT NULL DEFAULT 0"),
        ('extension_granted_at',     "ALTER TABLE `reports_report` ADD COLUMN `extension_granted_at` datetime(6) NULL"),
        ('extension_days',           "ALTER TABLE `reports_report` ADD COLUMN `extension_days` int UNSIGNED NOT NULL DEFAULT 0"),
    ]

    with connection.cursor() as cursor:
        for col, sql in fields_to_add:
            if col not in existing:
                cursor.execute(sql)


def reverse_fields(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0007_final_report_and_doi'),
    ]

    operations = [
        # Step 1: Add any missing columns to the DB (skips columns that already exist).
        migrations.RunPython(add_timeline_fields, reverse_fields),

        # Step 2: Sync Django's migration state without touching the DB.
        # SeparateDatabaseAndState lets us update the ORM state while using
        # no-op database_operations, since RunPython above already handled the DDL.
        migrations.SeparateDatabaseAndState(
            database_operations=[],   # DB already up-to-date via RunPython above
            state_operations=[
                migrations.AddField(
                    model_name='report',
                    name='submission_deadline',
                    field=models.DateTimeField(blank=True, null=True, help_text='Deadline for author resubmission'),
                ),
                migrations.AddField(
                    model_name='report',
                    name='reviewer_deadline',
                    field=models.DateTimeField(blank=True, null=True, help_text='Deadline for reviewer to complete review'),
                ),
                migrations.AddField(
                    model_name='report',
                    name='reminder_sent_at',
                    field=models.DateTimeField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='report',
                    name='extension_requested',
                    field=models.BooleanField(default=False),
                ),
                migrations.AddField(
                    model_name='report',
                    name='extension_request_reason',
                    field=models.TextField(blank=True),
                ),
                migrations.AddField(
                    model_name='report',
                    name='extension_requested_at',
                    field=models.DateTimeField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='report',
                    name='extension_granted',
                    field=models.BooleanField(default=False),
                ),
                migrations.AddField(
                    model_name='report',
                    name='extension_granted_at',
                    field=models.DateTimeField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='report',
                    name='extension_days',
                    field=models.PositiveIntegerField(default=0),
                ),
            ],
        ),
    ]
