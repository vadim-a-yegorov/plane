import hashlib
import hmac
import json

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from plane.app.permissions import ROLE, allow_permission
from plane.db.models import Project, TeamsChannelBinding, TeamsEmployee, User, Webhook, Workspace
from plane.services.relay_cards import channel_sink, dm_sink

from ..base import BaseAPIView


class TeamsRelayEndpoint(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = []

    def post(self, request):
        raw = request.body
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return Response({"error": "invalid json"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(payload, dict):
            payload = {}
        webhook_id = payload.get("webhook_id")
        webhook = None
        if webhook_id:
            try:
                webhook = Webhook.objects.filter(id=webhook_id).first()
            except (ValueError, ValidationError):
                webhook = None
        if not webhook or not webhook.secret_key:
            return Response({"error": "unknown webhook"}, status=status.HTTP_404_NOT_FOUND)
        signature = request.headers.get("X-Plane-Signature", "")
        expected = hmac.new(webhook.secret_key.encode("utf-8"), request.body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return Response({"error": "invalid signature"}, status=status.HTTP_403_FORBIDDEN)
        report = {}
        try:
            report["channel"] = channel_sink(payload)
        except Exception as exc:
            report["channel"] = str(exc)
        try:
            report["dm"] = dm_sink(payload)
        except Exception as exc:
            report["dm"] = str(exc)
        return Response(report, status=status.HTTP_200_OK)


class TeamsBindingEndpoint(BaseAPIView):
    @allow_permission(allowed_roles=[ROLE.ADMIN], level="WORKSPACE")
    def get(self, request, slug):
        rows = TeamsChannelBinding.objects.filter(workspace__slug=slug).select_related("project")
        data = [
            {
                "id": str(row.id),
                "project_id": str(row.project_id),
                "project_name": row.project.name if row.project else None,
                "team_id": row.team_id,
                "channel_id": row.channel_id,
            }
            for row in rows
        ]
        return Response(data, status=status.HTTP_200_OK)

    @allow_permission(allowed_roles=[ROLE.ADMIN], level="WORKSPACE")
    def post(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        project = Project.objects.filter(id=request.data.get("project_id"), workspace_id=workspace.id).first()
        if not project:
            return Response({"error": "project not found"}, status=status.HTTP_400_BAD_REQUEST)
        binding, _ = TeamsChannelBinding.objects.update_or_create(
            project_id=project.id,
            defaults={
                "workspace_id": workspace.id,
                "team_id": request.data.get("team_id") or None,
                "channel_id": request.data.get("channel_id") or None,
                "tenant_id": request.data.get("tenant_id") or None,
            },
        )
        return Response(
            {"id": str(binding.id), "project_id": str(binding.project_id)},
            status=status.HTTP_201_CREATED,
        )

    @allow_permission(allowed_roles=[ROLE.ADMIN], level="WORKSPACE")
    def delete(self, request, slug, pk=None):
        if not pk:
            return Response({"error": "binding id required"}, status=status.HTTP_400_BAD_REQUEST)
        binding = TeamsChannelBinding.objects.filter(id=pk, workspace__slug=slug).first()
        if not binding:
            return Response({"error": "binding not found"}, status=status.HTTP_404_NOT_FOUND)
        binding.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamsEmployeeEndpoint(BaseAPIView):
    @allow_permission(allowed_roles=[ROLE.ADMIN], level="WORKSPACE")
    def get(self, request, slug):
        rows = TeamsEmployee.objects.filter(binding__workspace__slug=slug).select_related("user", "binding__project")
        data = [
            {
                "id": str(row.id),
                "binding_id": str(row.binding_id),
                "project_id": str(row.binding.project_id),
                "oid": row.oid,
                "email": row.email,
                "user_id": str(row.user_id) if row.user_id else None,
                "has_conversation": bool((row.conversation_reference or {}).get("conversation")),
            }
            for row in rows
        ]
        return Response(data, status=status.HTTP_200_OK)

    @allow_permission(allowed_roles=[ROLE.ADMIN], level="WORKSPACE")
    def post(self, request, slug):
        binding = TeamsChannelBinding.objects.filter(
            id=request.data.get("binding_id"), workspace__slug=slug
        ).first()
        if not binding:
            return Response({"error": "binding not found"}, status=status.HTTP_404_NOT_FOUND)
        email = str(request.data.get("email") or "").lower() or None
        oid = request.data.get("oid") or None
        if not email and not oid:
            return Response({"error": "email or oid required"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=email).first() if email else None
        employee, _ = TeamsEmployee.objects.update_or_create(
            binding=binding,
            email=email,
            defaults={
                "oid": oid,
                "user": user,
                "conversation_reference": request.data.get("conversation_reference") or {},
            },
        )
        return Response(
            {
                "id": str(employee.id),
                "user_id": str(employee.user_id) if employee.user_id else None,
            },
            status=status.HTTP_201_CREATED,
        )
