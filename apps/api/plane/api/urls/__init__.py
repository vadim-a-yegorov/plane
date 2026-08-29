# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from .asset import urlpatterns as asset_patterns
from .member import urlpatterns as member_patterns
from .project import urlpatterns as project_patterns
from .state import urlpatterns as state_patterns
from .user import urlpatterns as user_patterns
from .work_item import urlpatterns as work_item_patterns
from .invite import urlpatterns as invite_patterns

urlpatterns = [
    *asset_patterns,
    *member_patterns,
    *project_patterns,
    *state_patterns,
    *user_patterns,
    *work_item_patterns,
    *invite_patterns,
]
