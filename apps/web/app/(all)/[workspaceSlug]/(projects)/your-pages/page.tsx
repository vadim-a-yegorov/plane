/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useEffect, useState } from "react";
import { Paperclip } from "lucide-react";
import { API_BASE_URL } from "@plane/constants";
import { LinkIcon, PageIcon } from "@plane/propel/icons";
import { cn, getFileURL } from "@plane/utils";
// components
import { PageHead } from "@/components/core/page-title";
// hooks
import { useAppRouter } from "@/hooks/use-app-router";
// services
import { APIService } from "@/services/api.service";

type TFlatEntry = {
  type: "page" | "file" | "link";
  id: string;
  name: string;
  href: string | null;
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

const TABS = [
  { key: "all", label: "All" },
  { key: "assigned", label: "Assigned to you" },
  { key: "created", label: "Created by you" },
  { key: "subscribed", label: "Subscribed" },
] as const;

function YourPagesRoot() {
  const router = useAppRouter();
  const [tab, setTab] = useState<string>("all");
  const [entries, setEntries] = useState<TFlatEntry[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    setEntries(null);
    setError(false);
    flatPagesService
      .getMyPages(tab)
      .then(setEntries)
      .catch(() => setError(true));
  }, [tab]);

  const openEntry = (entry: TFlatEntry) => {
    if (!entry.href) return;
    if (entry.type === "page") router.push(entry.href);
    else window.open(entry.type === "file" ? (getFileURL(entry.href) ?? entry.href) : entry.href, "_blank", "noopener");
  };

  return (
    <div className="flex h-full flex-col">
      <div className="border-default flex items-center gap-1 border-b px-4 py-2">
        {TABS.map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => setTab(t.key)}
            className={cn(
              "rounded-sm px-3 py-1 text-13 font-medium",
              tab === t.key ? "bg-layer-2 text-primary" : "text-secondary hover:bg-layer-1"
            )}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className="h-full overflow-y-auto">
        {error && <div className="text-sm text-red-500 p-4">Failed to load.</div>}
        {!error && entries === null && <div className="text-sm p-4 text-secondary">Loading...</div>}
        {entries?.length === 0 && <div className="text-sm p-4 text-secondary">Nothing here yet.</div>}
        {entries?.map((entry) => (
          <button
            key={`${entry.type}_${entry.id}`}
            type="button"
            onClick={() => openEntry(entry)}
            className="border-default flex w-full cursor-pointer items-center gap-2 border-b px-4 py-2 text-left hover:bg-layer-1"
          >
            {entry.type === "page" && <PageIcon className="h-3.5 w-3.5 flex-shrink-0" />}
            {entry.type === "file" && <Paperclip className="h-3.5 w-3.5 flex-shrink-0" />}
            {entry.type === "link" && <LinkIcon className="h-3.5 w-3.5 flex-shrink-0" />}
            <span className="text-sm truncate">{entry.name}</span>
            <span className="text-xs ml-auto flex-shrink-0 text-secondary">
              {new Date(entry.updated_at).toLocaleDateString()}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default function YourPagesPage() {
  return (
    <>
      <PageHead title="Your pages" />
      <div className="relative h-full w-full overflow-hidden overflow-y-auto">
        <YourPagesRoot />
      </div>
    </>
  );
}
