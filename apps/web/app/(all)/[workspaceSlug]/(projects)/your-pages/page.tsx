/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

// components
import { PageHead } from "@/components/core/page-title";
import { FlatPages, type TFlatPagesTab } from "./flat-pages";

export default function YourPagesPage() {
  return (
    <>
      <PageHead title="Pages" />
      <FlatPages tab="all" />
    </>
  );
}

export type { TFlatPagesTab };
