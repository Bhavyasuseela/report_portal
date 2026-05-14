"""
Migration 0009 — sync ORM state for publication/DOI fields.

Migration 0007 added the following columns to the DB via raw SQL (RunPython),
but never registered them in Django's migration state.  Django therefore tries
to add them again, causing a "Duplicate column name" error on MySQL.

This migration uses SeparateDatabaseAndState to record the fields in the ORM
state (so Django stops trying to create them) while performing *zero* DDL —
the columns already exist in the database.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0008_timeline_and_extensions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # No database operations — columns already exist from 0007 RunPython
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='report',
                    name='series_title',
                    field=models.CharField(blank=True, default='', max_length=300),
                ),
                migrations.AddField(
                    model_name='report',
                    name='series_number',
                    field=models.CharField(blank=True, default='', max_length=100),
                ),
                migrations.AddField(
                    model_name='report',
                    name='description',
                    field=models.TextField(blank=True, default=''),
                ),
                migrations.AddField(
                    model_name='report',
                    name='language',
                    field=models.CharField(blank=True, default='English', max_length=50),
                ),
                migrations.AddField(
                    model_name='report',
                    name='doi',
                    field=models.CharField(blank=True, default='', max_length=200),
                ),
                migrations.AddField(
                    model_name='report',
                    name='doi_assigned_at',
                    field=models.DateTimeField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='report',
                    name='doi_assigned_by',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='doi_assignments',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                migrations.AddField(
                    model_name='report',
                    name='final_report_requested_at',
                    field=models.DateTimeField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='report',
                    name='final_report_doc',
                    field=models.FileField(blank=True, null=True, upload_to='papers/final/'),
                ),
                migrations.AddField(
                    model_name='report',
                    name='final_report_notes',
                    field=models.TextField(blank=True, default=''),
                ),
                migrations.AddField(
                    model_name='report',
                    name='final_report_submitted_at',
                    field=models.DateTimeField(blank=True, null=True),
                ),
            ],
        ),
    ]
