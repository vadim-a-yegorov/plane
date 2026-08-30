from rest_framework.response import Response

from plane.app.views.base import BaseAPIView
from plane.db.models import Issue, Page, WorkspaceMember

LIMIT = 500


def _serialize(issue):
    return {
        "id": str(issue.id),
        "name": issue.name,
        "done": bool(issue.state_id and issue.state.group == "completed"),
        "state_id": str(issue.state_id) if issue.state_id else None,
        "project_id": str(issue.project_id),
        "workspace_slug": issue.workspace.slug,
        "assignees": [str(member.id) for member in issue.assignees.all()],
    }


def _issues_for(user):
    workspace_ids = WorkspaceMember.objects.filter(member=user, is_active=True).values_list(
        "workspace_id", flat=True
    )
    return (
        Issue.issue_objects.filter(workspace_id__in=workspace_ids)
        .select_related("state", "workspace")
        .prefetch_related("assignees")
        .order_by("-updated_at")
    )


def _done_filter(queryset, params):
    done = params.get("done")
    if done == "true":
        return queryset.filter(state__group="completed")
    if done == "false":
        return queryset.exclude(state__group="completed")
    return queryset


class MyWorkEndpoint(BaseAPIView):
    def get(self, request):
        issues = _done_filter(_issues_for(request.user).filter(assignees=request.user), request.query_params)[
            :LIMIT
        ]
        return Response([_serialize(issue) for issue in issues])


class AllWorkEndpoint(BaseAPIView):
    def get(self, request):
        issues = _done_filter(_issues_for(request.user), request.query_params)[:LIMIT]
        return Response([_serialize(issue) for issue in issues])


class MyPagesEndpoint(BaseAPIView):
    def get(self, request):
        workspace_ids = WorkspaceMember.objects.filter(member=request.user, is_active=True).values_list(
            "workspace_id", flat=True
        )
        pages = (
            Page.objects.filter(workspace_id__in=workspace_ids)
            .select_related("workspace", "owned_by")
            .prefetch_related("projects")
            .order_by("-updated_at")[:LIMIT]
        )
        return Response(
            [
                {
                    "type": "page",
                    "id": str(page.id),
                    "name": page.name,
                    "href": f"/{page.workspace.slug}/projects/{page.projects.first().id if page.projects.exists() else ''}/pages/{page.id}/",
                    "project_id": str(page.projects.first().id) if page.projects.exists() else None,
                    "created_by": str(page.owned_by_id),
                    "updated_at": page.updated_at.isoformat(),
                }
                for page in pages
            ]
        )
