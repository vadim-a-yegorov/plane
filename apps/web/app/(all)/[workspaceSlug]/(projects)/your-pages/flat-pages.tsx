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
// hooks
import { useAppRouter } from "@/hooks/use-app-router";
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
    <div ref={parentRef} className="h-full overflow-y-auto px-3 py-2">
      {entries.map((entry) => {
        const Icon = entry.type === "page" ? PageIcon : entry.type === "file" ? Paperclip : LinkIcon;
        return (
          <div
            key={`${entry.type}_${entry.id}`}
            onClick={() => openEntry(entry)}
            className="group relative flex w-full cursor-pointer items-center justify-between gap-3 rounded-lg border border-subtle bg-layer-1 px-4 py-3 mb-2 hover:bg-layer-1-hover hover:border-strong active:bg-layer-1-active transition-all shadow-sm"
          >
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <div className="flex h-8 w-8 items-center justify-center rounded-md bg-layer-2 flex-shrink-0">
                <Icon className="h-4 w-4 text-tertiary" />
              </div>
              <span className="truncate text-sm font-medium text-primary">{entry.name}</span>
            </div>
            <span className="text-xs text-secondary flex-shrink-0">
              {new Date(entry.updated_at).toLocaleDateString()}
            </span>
          </div>
        );
      })}
    </div>
  );
}
