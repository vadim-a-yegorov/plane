/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

// components
import { PageHead } from "@/components/core/page-title";
import type { Route } from "./+types/page";
import { FlatPages, type TFlatPagesTab } from "../flat-pages";

const TABS: readonly TFlatPagesTab[] = new Set(["assigned", "created", "subscribed"]);

export default function YourPagesTabPage({ params }: Route.ComponentProps) {
  const { tabId } = params;

  if (!TABS.has(tabId as TFlatPagesTab)) return null;

  return (
    <>
      <PageHead title={`Pages - ${tabId}`} />
      <FlatPages tab={tabId as TFlatPagesTab} />
    </>
  );
}
