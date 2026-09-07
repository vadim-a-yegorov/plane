# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from datetime import datetime

from rest_framework import status
from rest_framework.response import Response

from plane.api.views.base import BaseAPIView
from plane.app.permissions import ProjectEntityPermission, WorkspaceEntityPermission
from plane.app.serializers import PageDetailSerializer, PageSerializer
from plane.bgtasks.page_transaction_task import page_transaction
from plane.db.models import Issue, Page, PageLog, Project, ProjectPage, Workspace


def _page_queryset(slug, project_id=None):
    qs = Page.objects.filter(workspace__slug=slug).select_related("workspace", "owned_by").prefetch_related("projects")
    if project_id:
        qs = qs.filter(projects__id=project_id, project_pages__deleted_at__isnull=True)
    return qs.distinct()


class PageListCreateAPIEndpoint(BaseAPIView):
    """API-key CRUD for project pages. Mounted at /api/v1/workspaces/{slug}/projects/{project_id}/pages/."""

    serializer_class = PageDetailSerializer
    model = Page
    permission_classes = [ProjectEntityPermission]
    use_read_replica = True

    def get_queryset(self):
        return _page_queryset(self.kwargs.get("slug"), self.kwargs.get("project_id"))

    def get(self, request, slug, project_id):
        return self.paginate(
            request=request,
            queryset=self.get_queryset().order_by("-created_at"),
            on_results=lambda pages: PageDetailSerializer(pages, many=True).data,
        )

    def post(self, request, slug, project_id):
        Project.objects.get(pk=project_id, workspace__slug=slug)
        serializer = PageSerializer(
            data=request.data,
            context={
                "project_id": project_id,
                "owned_by_id": request.user.id,
                "description_json": request.data.get("description_json", {}),
                "description_binary": request.data.get("description_binary", None),
                "description_html": request.data.get("description_html", "<p></p>"),
            },
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        page_transaction.delay(
            new_description_html=request.data.get("description_html", "<p></p>"),
            old_description_html=None,
            page_id=serializer.data["id"],
        )
        page = self.get_queryset().get(pk=serializer.data["id"])
        return Response(PageDetailSerializer(page).data, status=status.HTTP_201_CREATED)


class PageDetailAPIEndpoint(BaseAPIView):
    serializer_class = PageDetailSerializer
    model = Page
    permission_classes = [ProjectEntityPermission]
    use_read_replica = True

    def get_queryset(self):
        return _page_queryset(self.kwargs.get("slug"), self.kwargs.get("project_id"))

    def _page(self, page_id):
        return self.get_queryset().get(pk=page_id)

    def get(self, request, slug, project_id, page_id):
        return Response(PageDetailSerializer(self._page(page_id)).data, status=status.HTTP_200_OK)

    def patch(self, request, slug, project_id, page_id):
        page = self._page(page_id)
        if page.is_locked:
            return Response({"error": "Page is locked"}, status=status.HTTP_400_BAD_REQUEST)
        old_html = page.description_html
        serializer = PageDetailSerializer(page, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        if request.data.get("description_html"):
            page_transaction.delay(
                new_description_html=request.data.get("description_html"),
                old_description_html=old_html,
                page_id=str(page_id),
            )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slug, project_id, page_id):
        self._page(page_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PageArchiveAPIEndpoint(BaseAPIView):
    permission_classes = [ProjectEntityPermission]
    model = Page

    def post(self, request, slug, project_id, page_id):
        page = _page_queryset(slug, project_id).get(pk=page_id)
        now = datetime.now()
        page.archived_at = now.date()
        page.save(update_fields=["archived_at"])
        return Response({"archived_at": str(now)}, status=status.HTTP_200_OK)

    def delete(self, request, slug, project_id, page_id):
        page = _page_queryset(slug, project_id).get(pk=page_id)
        page.archived_at = None
        page.save(update_fields=["archived_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkspacePageListCreateAPIEndpoint(BaseAPIView):
    """API-key CRUD for workspace pages at /api/v1/workspaces/{slug}/pages/."""

    serializer_class = PageDetailSerializer
    model = Page
    permission_classes = [WorkspaceEntityPermission]
    use_read_replica = True

    def get_queryset(self):
        return _page_queryset(self.kwargs.get("slug")).order_by("-created_at")

    def get(self, request, slug):
        return self.paginate(
            request=request,
            queryset=self.get_queryset(),
            on_results=lambda pages: PageDetailSerializer(pages, many=True).data,
        )

    def post(self, request, slug):
        workspace = Workspace.objects.get(slug=slug)
        project_id = request.data.get("project_id")
        if project_id:
            serializer = PageSerializer(
                data=request.data,
                context={
                    "project_id": project_id,
                    "owned_by_id": request.user.id,
                    "description_json": request.data.get("description_json", {}),
                    "description_binary": request.data.get("description_binary", None),
                    "description_html": request.data.get("description_html", "<p></p>"),
                },
            )
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            page = Page.objects.get(pk=serializer.data["id"])
        else:
            page = Page.objects.create(
                name=request.data.get("name", ""),
                description_html=request.data.get("description_html", "<p></p>"),
                owned_by_id=request.user.id,
                workspace_id=workspace.id,
                is_global=True,
                access=request.data.get("access", 0),
                color=request.data.get("color", ""),
            )
        page_transaction.delay(
            new_description_html=request.data.get("description_html", "<p></p>"),
            old_description_html=None,
            page_id=str(page.id),
        )
        return Response(PageDetailSerializer(page).data, status=status.HTTP_201_CREATED)


class WorkspacePageDetailAPIEndpoint(BaseAPIView):
    serializer_class = PageDetailSerializer
    model = Page
    permission_classes = [WorkspaceEntityPermission]
    use_read_replica = True

    def get(self, request, slug, page_id):
        page = _page_queryset(slug).get(pk=page_id)
        return Response(PageDetailSerializer(page).data, status=status.HTTP_200_OK)

    def patch(self, request, slug, page_id):
        page = _page_queryset(slug).get(pk=page_id)
        old_html = page.description_html
        serializer = PageDetailSerializer(page, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        if request.data.get("description_html"):
            page_transaction.delay(
                new_description_html=request.data.get("description_html"),
                old_description_html=old_html,
                page_id=str(page_id),
            )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slug, page_id):
        _page_queryset(slug).get(pk=page_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkItemPageListCreateAPIEndpoint(BaseAPIView):
    """Link a page to a work item. POST {page_id}."""

    permission_classes = [ProjectEntityPermission]
    model = PageLog

    def get(self, request, slug, project_id, issue_id):
        Issue.objects.get(pk=issue_id, project_id=project_id, workspace__slug=slug)
        logs = PageLog.objects.filter(
            workspace__slug=slug,
            entity_name="issue",
            entity_identifier=issue_id,
        ).select_related("page")
        results = [
            {
                "id": str(log.id),
                "issue": str(issue_id),
                "project": str(project_id),
                "workspace": str(log.workspace_id),
                "created_at": log.created_at.isoformat() if log.created_at else None,
                "updated_at": log.updated_at.isoformat() if log.updated_at else None,
                "created_by": str(log.created_by_id) if log.created_by_id else None,
                "page": {
                    "id": str(log.page_id),
                    "name": log.page.name,
                    "is_global": log.page.is_global,
                    "logo_props": log.page.logo_props,
                    "created_at": log.page.created_at.isoformat() if log.page.created_at else None,
                    "updated_at": log.page.updated_at.isoformat() if log.page.updated_at else None,
                    "created_by": str(log.page.created_by_id) if log.page.created_by_id else None,
                },
            }
            for log in logs
        ]
        return Response({"results": results, "count": len(results)}, status=status.HTTP_200_OK)

    def post(self, request, slug, project_id, issue_id):
        issue = Issue.objects.get(pk=issue_id, project_id=project_id, workspace__slug=slug)
        page_id = request.data.get("page_id")
        if not page_id:
            return Response({"error": "page_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        page = Page.objects.get(pk=page_id, workspace__slug=slug)
        log = PageLog.objects.create(
            page=page,
            entity_name="issue",
            entity_identifier=issue.id,
            workspace_id=issue.workspace_id,
        )
        return Response(
            {
                "id": str(log.id),
                "issue": str(issue.id),
                "project": str(project_id),
                "workspace": str(log.workspace_id),
                "page": {"id": str(page.id), "name": page.name, "is_global": page.is_global},
            },
            status=status.HTTP_201_CREATED,
        )


class WorkItemPageDetailAPIEndpoint(BaseAPIView):
    permission_classes = [ProjectEntityPermission]
    model = PageLog

    def delete(self, request, slug, project_id, issue_id, work_item_page_id):
        PageLog.objects.get(
            pk=work_item_page_id,
            workspace__slug=slug,
            entity_name="issue",
            entity_identifier=issue_id,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)