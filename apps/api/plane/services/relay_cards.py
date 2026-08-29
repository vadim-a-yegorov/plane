import logging
import time

from django.conf import settings

from plane.db.models import Project, TeamsChannelBinding, TeamsEmployee, User
from plane.utils.url_security import pinned_fetch

logger = logging.getLogger("plane.worker")

_TOKEN = {"value": None, "expires": 0.0}


def web_base():
    return (settings.WEB_URL or "http://localhost").rstrip("/")


def bot_configured():
    return bool(settings.MS_APP_ID and settings.MS_APP_PASSWORD)


def bot_token():
    now = time.time()
    if _TOKEN["value"] and now < _TOKEN["expires"]:
        return _TOKEN["value"]
    resp = pinned_fetch(
        "POST",
        "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token",
        data={
            "grant_type": "client_credentials",
            "client_id": settings.MS_APP_ID,
            "client_secret": settings.MS_APP_PASSWORD,
            "scope": "https://api.botframework.com/.default",
        },
        timeout=15,
    )
    resp.raise_for_status()
    body = resp.json()
    _TOKEN["value"] = body["access_token"]
    _TOKEN["expires"] = now + int(body.get("expires_in", 3600)) - 60
    return _TOKEN["value"]


def channel_conversation_id(binding):
    if binding.conversation_id:
        return binding.conversation_id, binding.service_url or settings.MS_BOT_SERVICE_URL
    service_url = binding.service_url or settings.MS_BOT_SERVICE_URL
    resp = pinned_fetch(
        "POST",
        f"{service_url.rstrip('/')}/v3/conversations",
        headers={"Authorization": f"Bearer {bot_token()}"},
        json={"channelId": binding.channel_id, "tenantId": binding.tenant_id},
        timeout=15,
    )
    resp.raise_for_status()
    binding.conversation_id = resp.json()["id"]
    binding.service_url = service_url
    binding.save()
    return binding.conversation_id, service_url


def post_activity(service_url, conversation_id, activity):
    url = f"{service_url.rstrip('/')}/v3/conversations/{conversation_id}/activities"
    resp = pinned_fetch(
        "POST",
        url,
        headers={"Authorization": f"Bearer {bot_token()}"},
        json=activity,
        timeout=15,
    )
    resp.raise_for_status()
    return resp


def board_link(slug, project_id):
    return f"{web_base()}/{slug}/projects/{project_id}/issues/?layout=kanban"


def item_link(slug, project_id, issue_id):
    return f"{web_base()}/{slug}/projects/{project_id}/issues/{issue_id}/"


def assignee_emails(data):
    out = set()
    raw = data.get("assignees")
    if isinstance(raw, list):
        for entry in raw:
            if isinstance(entry, dict) and entry.get("email"):
                out.add(str(entry["email"]).lower())
    if out:
        return out
    ids = data.get("assignee_ids") or []
    if ids:
        rows = User.objects.filter(id__in=ids).exclude(email__isnull=True).values_list("email", flat=True)
        out.update(str(email).lower() for email in rows if email)
    return out


def channel_sink(payload):
    if not bot_configured():
        return "bot not configured"
    data = payload.get("data") or {}
    slug = payload.get("workspace_slug")
    project_id = data.get("project_id") or data.get("project")
    if not slug or not project_id:
        return "no project in payload"
    binding = TeamsChannelBinding.objects.filter(workspace__slug=slug, project_id=project_id).first()
    if not binding or not binding.channel_id:
        return "no channel binding"
    name = data.get("name") or data.get("title") or "Work item"
    project_name = Project.objects.filter(id=project_id).values_list("name", flat=True).first() or "project"
    action = payload.get("action") or "update"
    event = payload.get("event") or "item"
    text = f"{name} — {action} ({event}, {project_name})"
    open_url = item_link(slug, project_id, data.get("id")) if data.get("id") else board_link(slug, project_id)
    card = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "title": name,
        "text": text,
        "summary": text,
        "potentialAction": [
            {"@type": "OpenUri", "name": "Open board", "targets": [{"os": "default", "uri": open_url}]}
        ],
    }
    activity = {
        "type": "message",
        "text": text,
        "attachments": [{"contentType": "application/vnd.microsoft.card.messagecard", "content": card}],
        "channelData": {"teamsChannelId": binding.channel_id},
    }
    conversation_id, service_url = channel_conversation_id(binding)
    post_activity(service_url, conversation_id, activity)
    return None


def dm_sink(payload):
    if not bot_configured():
        return "bot not configured"
    data = payload.get("data") or {}
    slug = payload.get("workspace_slug")
    project_id = data.get("project_id") or data.get("project")
    emails = assignee_emails(data)
    if not emails:
        return "no assignees"
    employees = TeamsEmployee.objects.filter(
        binding__workspace__slug=slug,
        binding__project_id=project_id,
        email__in=sorted(emails),
    ).select_related("binding")
    if not employees:
        return "assignees not registered"
    name = data.get("name") or data.get("title") or "Work item"
    action = payload.get("action") or "update"
    text = f"{name} was {action}d and is assigned to you."
    open_url = item_link(slug, project_id, data.get("id")) if data.get("id") else board_link(slug, project_id)
    activity = {
        "type": "message",
        "text": text,
        "suggestedActions": {"actions": [{"type": "openUrl", "title": "Open item", "value": open_url}]},
    }
    errors = []
    for emp in employees:
        ref = emp.conversation_reference or {}
        conversation = ref.get("conversation") or {}
        if not conversation.get("id"):
            errors.append(f"{emp.email}: no conversationReference")
            continue
        service_url = ref.get("serviceUrl") or settings.MS_BOT_SERVICE_URL
        try:
            post_activity(service_url, conversation["id"], activity)
        except Exception as exc:
            errors.append(f"{emp.email}: {exc}")
    return "; ".join(errors) if errors else None
