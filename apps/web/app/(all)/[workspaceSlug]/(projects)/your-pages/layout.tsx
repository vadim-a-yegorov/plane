/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { Outlet } from "react-router";
import { useTranslation } from "@plane/i18n";
import { PageIcon } from "@plane/propel/icons";
import { Breadcrumbs, Header } from "@plane/ui";
// components
import { AppHeader } from "@/components/core/app-header";
import { ContentWrapper } from "@/components/core/content-wrapper";
import { BreadcrumbLink } from "@/components/common/breadcrumb-link";

function YourPagesHeader() {
  const { t } = useTranslation();
  return (
    <Header>
      <Header.LeftItem>
        <div className="flex items-center gap-2.5">
          <Breadcrumbs>
            <Breadcrumbs.Item
              component={<BreadcrumbLink label={t("pages")} icon={<PageIcon className="h-4 w-4 text-tertiary" />} />}
            />
          </Breadcrumbs>
        </div>
      </Header.LeftItem>
    </Header>
  );
}

export default function YourPagesLayout() {
  return (
    <>
      <AppHeader header={<YourPagesHeader />} />
      <ContentWrapper>
        <Outlet />
      </ContentWrapper>
    </>
  );
}
