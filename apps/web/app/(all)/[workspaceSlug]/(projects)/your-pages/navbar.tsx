/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
// plane imports
import { Header, EHeaderVariant } from "@plane/ui";
import { cn } from "@plane/utils";

export const YOUR_PAGES_TABS = [
  { key: "all", label: "All" },
  { key: "assigned", label: "Assigned to you" },
  { key: "created", label: "Created by you" },
  { key: "subscribed", label: "Subscribed" },
] as const;

export function YourPagesNavbar() {
  const { workspaceSlug } = useParams();
  const pathname = usePathname();

  return (
    <Header variant={EHeaderVariant.SECONDARY} showOnMobile={false}>
      <div className="flex items-center overflow-x-scroll">
        {YOUR_PAGES_TABS.map((tab) => {
          const href = tab.key === "all" ? `/${workspaceSlug}/your-pages` : `/${workspaceSlug}/your-pages/${tab.key}`;
          const isActive =
            tab.key === "all"
              ? pathname === `/${workspaceSlug}/your-pages` || pathname === `/${workspaceSlug}/your-pages/`
              : pathname.startsWith(`/${workspaceSlug}/your-pages/${tab.key}`);
          return (
            <Link key={tab.key} href={href}>
              <span
                className={cn(
                  `flex border-b-2 p-4 text-13 font-medium whitespace-nowrap text-tertiary outline-none hover:text-primary ${
                    isActive
                      ? "border-accent-strong text-accent-primary hover:text-accent-primary"
                      : "border-transparent"
                  }`
                )}
              >
                {tab.label}
              </span>
            </Link>
          );
        })}
      </div>
    </Header>
  );
}
