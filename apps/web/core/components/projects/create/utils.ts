/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type { IProject } from "@plane/types";

export const getProjectFormValues = (): Partial<IProject> => ({
  description: "",
  identifier: "",
  name: "",
  network: 2,
  project_lead: null,
});
