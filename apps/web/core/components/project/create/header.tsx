/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { ETabIndices } from "@plane/constants";
import { CloseIcon } from "@plane/propel/icons";
import { getTabIndex } from "@plane/utils";

type Props = {
  handleClose: () => void;
  isMobile?: boolean;
  handleFormOnChange?: () => void;
  isClosable?: boolean;
  handleTemplateSelect?: () => void;
  showActionButtons?: boolean;
};

function ProjectCreateHeader(props: Props) {
  const { handleClose, isMobile = false, isClosable = true } = props;
  const { getIndex } = getTabIndex(ETabIndices.PROJECT_CREATE, isMobile);

  return (
    <div className="relative h-10 w-full">
      {isClosable && (
        <div className="absolute top-0 right-0 p-2">
          <button type="button" onClick={handleClose} tabIndex={getIndex("close")}>
            <CloseIcon className="h-5 w-5" />
          </button>
        </div>
      )}
    </div>
  );
}

export default ProjectCreateHeader;
