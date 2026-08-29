import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0123_project_calendar_enabled"),
    ]

    operations = [
        migrations.CreateModel(
            name="TeamsChannelBinding",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("deleted_at", models.DateTimeField(blank=True, null=True, verbose_name="Deleted At")),
                ("team_id", models.CharField(blank=True, max_length=255, null=True)),
                ("channel_id", models.CharField(blank=True, max_length=255, null=True)),
                ("tenant_id", models.CharField(blank=True, max_length=255, null=True)),
                ("service_url", models.CharField(blank=True, max_length=500, null=True)),
                ("conversation_id", models.CharField(blank=True, max_length=500, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to="db.user",
                        verbose_name="Created By",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated_by",
                        to="db.user",
                        verbose_name="Last Modified By",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teams_bindings",
                        to="db.project",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teams_bindings",
                        to="db.workspace",
                    ),
                ),
            ],
            options={
                "db_table": "teams_channel_bindings",
            },
        ),
        migrations.CreateModel(
            name="TeamsEmployee",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Last Modified At")),
                ("deleted_at", models.DateTimeField(blank=True, null=True, verbose_name="Deleted At")),
                ("oid", models.CharField(blank=True, max_length=255, null=True)),
                ("email", models.EmailField(blank=True, max_length=255, null=True)),
                ("conversation_reference", models.JSONField(default=dict)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to="db.user",
                        verbose_name="Created By",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated_by",
                        to="db.user",
                        verbose_name="Last Modified By",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="teams_profiles",
                        to="db.user",
                    ),
                ),
                (
                    "binding",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="employees",
                        to="db.teamschannelbinding",
                    ),
                ),
            ],
            options={
                "db_table": "teams_employees",
            },
        ),
        migrations.AddConstraint(
            model_name="teamschannelbinding",
            constraint=models.UniqueConstraint(
                condition=models.Q(("deleted_at__isnull", True)),
                fields=["project"],
                name="teams_binding_unique_project_when_active",
            ),
        ),
        migrations.AddConstraint(
            model_name="teamsemployee",
            constraint=models.UniqueConstraint(
                condition=models.Q(("deleted_at__isnull", True), ("email__isnull", False)),
                fields=["binding", "email"],
                name="teams_employee_unique_binding_email",
            ),
        ),
    ]
