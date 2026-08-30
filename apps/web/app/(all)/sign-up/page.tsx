/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

// components
import { AuthBase } from "@/components/auth-screens/auth-base";
// helpers
import { EAuthModes, EPageTypes } from "@/helpers/authentication.helper";
// assets
import DefaultLayout from "@/layouts/default-layout";
import { AuthenticationWrapper } from "@/lib/wrappers/authentication-wrapper";

function SignUpPage() {
  return (
    <DefaultLayout>
      <AuthenticationWrapper pageType={EPageTypes.NON_AUTHENTICATED}>
        <div className="flex h-screen w-full items-center justify-center">
          <div className="text-center">
            <p className="text-secondary">Sign-up is disabled. Contact your administrator.</p>
            <a href="/sign-in/" className="text-primary hover:underline mt-4 inline-block">Go to sign-in</a>
          </div>
        </div>
      </AuthenticationWrapper>
    </DefaultLayout>
  );
}

export default SignUpPage;
