from django.db import models

from plane.db.models import BaseModel


class TeamsChannelBinding(BaseModel):
    workspace = models.ForeignKey("db.Workspace", on_delete=models.CASCADE, related_name="teams_bindings")
    project = models.ForeignKey("db.Project", on_delete=models.CASCADE, related_name="teams_bindings")
    team_id = models.CharField(max_length=255, blank=True, null=True)
    channel_id = models.CharField(max_length=255, blank=True, null=True)
    tenant_id = models.CharField(max_length=255, blank=True, null=True)
    service_url = models.CharField(max_length=500, blank=True, null=True)
    conversation_id = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "teams_channel_bindings"
        constraints = [
            models.UniqueConstraint(
                fields=["project"],
                condition=models.Q(deleted_at__isnull=True),
                name="teams_binding_unique_project_when_active",
            )
        ]


class TeamsEmployee(BaseModel):
    binding = models.ForeignKey(TeamsChannelBinding, on_delete=models.CASCADE, related_name="employees")
    user = models.ForeignKey("db.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="teams_profiles")
    oid = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    conversation_reference = models.JSONField(default=dict)

    class Meta:
        db_table = "teams_employees"
        constraints = [
            models.UniqueConstraint(
                fields=["binding", "email"],
                condition=models.Q(deleted_at__isnull=True, email__isnull=False),
                name="teams_employee_unique_binding_email",
            )
        ]
