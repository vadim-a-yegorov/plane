/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useRef } from "react";
import { Paperclip } from "lucide-react";
import useSWR from "swr";
// plane imports
import { API_BASE_URL } from "@plane/constants";
import { LinkIcon, PageIcon } from "@plane/propel/icons";
import { getFileURL } from "@plane/utils";
// components
import { ListItem } from "@/components/core/list";
// hooks
import { useAppRouter } from "@/hooks/use-app-router";
import { usePlatformOS } from "@/hooks/use-platform-os";
// services
import { APIService } from "@/services/api.service";

export type TFlatPagesTab = "all" | "assigned" | "created" | "subscribed";

type TFlatEntry = {
  type: "page" | "file" | "link";
  id: string;
  name: string;
  href: string | null;
  project_ids?: string[];
  project_id?: string | null;
  issue_id?: string | null;
  created_by?: string;
  updated_at: string;
};

class FlatPagesService extends APIService {
  constructor() {
    super(API_BASE_URL);
  }

  async getMyPages(tab: string): Promise<TFlatEntry[]> {
    return this.get(`/api/pages/my/`, {
      params: { tab },
    })
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}

const flatPagesService = new FlatPagesService();

export function FlatPages({ tab }: { tab: TFlatPagesTab }) {
  const router = useAppRouter();
  const parentRef = useRef<HTMLDivElement>(null);
  const { isMobile } = usePlatformOS();
  const { data: entries, error } = useSWR(`FLAT_PAGES_${tab}`, () => flatPagesService.getMyPages(tab), {
    revalidateIfStale: false,
    revalidateOnFocus: false,
  });

  const openEntry = (entry: TFlatEntry) => {
    if (!entry.href) return;
    if (entry.type === "page") router.push(entry.href);
    else window.open(entry.type === "file" ? (getFileURL(entry.href) ?? entry.href) : entry.href, "_blank", "noopener");
  };

  if (error) return <div className="text-sm text-red-500 p-4">Failed to load.</div>;
  if (!entries) return <div className="text-sm p-4 text-secondary">Loading...</div>;
  if (entries.length === 0) return <div className="text-sm p-4 text-secondary">Nothing here yet.</div>;

  return (
    <div ref={parentRef} className="h-full overflow-y-auto">
      {entries.map((entry) => (
        <ListItem
          key={`${entry.type}_${entry.id}`}
          title={entry.name}
          itemLink={entry.href || "#"}
          onItemClick={(e) => {
            e.preventDefault();
            openEntry(entry);
          }}
          prependTitleElement={
            entry.type === "page" ? (
              <PageIcon className="h-4 w-4 text-tertiary" />
            ) : entry.type === "file" ? (
              <Paperclip className="h-4 w-4 text-tertiary" />
            ) : (
              <LinkIcon className="h-4 w-4 text-tertiary" />
            )
          }
          appendTitleElement={
            <span className="text-xs text-secondary flex-shrink-0">
              {new Date(entry.updated_at).toLocaleDateString()}
            </span>
          }
          isMobile={isMobile}
          parentRef={parentRef}
        />
      ))}
    </div>
  );
}
