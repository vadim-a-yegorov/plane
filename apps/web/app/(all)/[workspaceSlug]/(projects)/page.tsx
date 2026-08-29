/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import { Navigate, useParams } from "react-router";
// hooks
import { useUser } from "@/hooks/store/user";

const WorkspaceIndexPage = observer(function WorkspaceIndexPage() {
  const { workspaceSlug } = useParams();
  const { data: currentUser } = useUser();

  if (!currentUser?.id) return null;

  return <Navigate to={`/${workspaceSlug}/profile/${currentUser.id}/`} replace />;
});

export default WorkspaceIndexPage;
