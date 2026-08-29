# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from .api import urlpatterns as api_urls
from .asset import urlpatterns as asset_urls
from .issue import urlpatterns as issue_urls
from .page import urlpatterns as page_urls
from .project import urlpatterns as project_urls
from .search import urlpatterns as search_urls
from .state import urlpatterns as state_urls
from .user import urlpatterns as user_urls
from .workspace import urlpatterns as workspace_urls
from .timezone import urlpatterns as timezone_urls
from .flat import urlpatterns as flat_urls
from .webhook import urlpatterns as webhook_urls

urlpatterns = [
    *asset_urls,
    *issue_urls,
    *page_urls,
    *project_urls,
    *search_urls,
    *state_urls,
    *user_urls,
    *workspace_urls,
    *api_urls,
    *timezone_urls,
    *flat_urls,
    *webhook_urls,
]
