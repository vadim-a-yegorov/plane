# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.urls import path


from plane.space.views import (
    IssueRetrievePublicEndpoint,
    IssueReactionPublicViewSet,
    IssueVotePublicViewSet,
)

urlpatterns = [
    path(
        "anchor/<str:anchor>/issues/<uuid:issue_id>/",
        IssueRetrievePublicEndpoint.as_view(),
        name="workspace-project-boards",
    ),
    path(
        "anchor/<str:anchor>/issues/<uuid:issue_id>/reactions/",
        IssueReactionPublicViewSet.as_view({"get": "list", "post": "create"}),
        name="issue-reactions-project-board",
    ),
    path(
        "anchor/<str:anchor>/issues/<uuid:issue_id>/reactions/<str:reaction_code>/",
        IssueReactionPublicViewSet.as_view({"delete": "destroy"}),
        name="issue-reactions-project-board",
    ),
    path(
        "anchor/<str:anchor>/issues/<uuid:issue_id>/votes/",
        IssueVotePublicViewSet.as_view({"get": "list", "post": "create", "delete": "destroy"}),
        name="issue-vote-project-board",
    ),
]
