from django.db.models import Q
from rest_framework.response import Response

from plane.app.views.base import BaseAPIView
from plane.db.models import FileAsset, Issue, IssueLink, Page, PageLog, UserFavorite, WorkspaceMember

LIMIT = 500
PAGES_LIMIT = 500


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


def _page_entry(page):
    project_ids = [str(project_id) for project_id in page.projects.values_list("id", flat=True)]
    return {
        "type": "page",
        "id": str(page.id),
        "name": page.name,
        "href": f"/{page.workspace.slug}/projects/{project_ids[0]}/pages/{page.id}" if project_ids else None,
        "project_ids": project_ids,
        "created_by": str(page.owned_by_id),
        "updated_at": page.updated_at,
    }


def _file_entry(asset):
    attributes = asset.attributes or {}
    return {
        "type": "file",
        "id": str(asset.id),
        "name": attributes.get("name") or "File",
        "href": asset.asset_url,
        "project_id": str(asset.project_id) if asset.project_id else None,
        "issue_id": str(asset.issue_id) if asset.issue_id else None,
        "created_by": str(asset.user_id or asset.created_by_id),
        "updated_at": asset.updated_at,
    }


def _link_entry(link):
    return {
        "type": "link",
        "id": str(link.id),
        "name": link.title or link.url,
        "href": link.url,
        "project_id": str(link.project_id),
        "issue_id": str(link.issue_id),
        "created_by": str(link.created_by_id),
        "updated_at": link.updated_at,
    }


class MyPagesEndpoint(BaseAPIView):
    def get(self, request):
        tab = request.query_params.get("tab", "all")
        workspace_ids = WorkspaceMember.objects.filter(member=request.user, is_active=True).values_list(
            "workspace_id", flat=True
        )
        attachment_type = FileAsset.EntityTypeContext.ISSUE_ATTACHMENT

        if tab == "created":
            pages = Page.objects.filter(workspace_id__in=workspace_ids, owned_by=request.user)
            files = FileAsset.objects.filter(
                workspace_id__in=workspace_ids, user=request.user, entity_type=attachment_type, is_deleted=False
            )
            links = IssueLink.objects.filter(workspace_id__in=workspace_ids, created_by=request.user)
        elif tab == "assigned":
            issue_ids = Issue.issue_objects.filter(
                workspace_id__in=workspace_ids, assignees=request.user
            ).values_list("id", flat=True)
            page_ids = (
                PageLog.objects.filter(
                    workspace_id__in=workspace_ids, entity_name="issue", entity_identifier__in=issue_ids
                )
                .values_list("page_id", flat=True)
                .distinct()
            )
            pages = Page.objects.filter(id__in=page_ids)
            files = FileAsset.objects.filter(issue_id__in=issue_ids, entity_type=attachment_type, is_deleted=False)
            links = IssueLink.objects.filter(issue_id__in=issue_ids)
        elif tab == "subscribed":
            favorite_page_ids = UserFavorite.objects.filter(
                user=request.user, workspace_id__in=workspace_ids, entity_type="page"
            ).values_list("entity_identifier", flat=True)
            pages = Page.objects.filter(id__in=favorite_page_ids)
            files = FileAsset.objects.none()
            links = IssueLink.objects.none()
        else:
            pages = Page.objects.filter(
                Q(owned_by=request.user) | Q(access=0), workspace_id__in=workspace_ids, archived_at__isnull=True
            )
            files = FileAsset.objects.filter(
                workspace_id__in=workspace_ids, entity_type=attachment_type, is_deleted=False
            )
            links = IssueLink.objects.filter(workspace_id__in=workspace_ids)

        pages = pages.select_related("workspace").prefetch_related("projects").order_by("-updated_at")[:PAGES_LIMIT]
        files = files.order_by("-updated_at")[:PAGES_LIMIT]
        links = links.order_by("-created_at")[:PAGES_LIMIT]

        entries = [_page_entry(page) for page in pages]
        entries += [_file_entry(asset) for asset in files]
        entries += [_link_entry(link) for link in links]
        entries.sort(key=lambda entry: entry["updated_at"], reverse=True)
        return Response(entries)
