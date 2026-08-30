# Plane → flat team tracker (yourprogress.app pattern)

All reasoning for this fork lives here. Code carries no comments.

## Locked model

1. ONE workspace. Creation endpoint returns 403 unconditionally.
2. N projects under it. Selecting a project switches BOTH the board and the documents, /company/q3/board ↔ /company/q3/documents pattern. One context switch, two surfaces follow.
3. Task = title + done + assignee. No description field, no comments, no attachments surface. Decomposition only via subtasks (parent_id stays). Dates exist ONLY on calendar-enabled projects.
4. Calendar: Project.calendar_enabled BooleanField, default False, admin-toggled. When False, any start_date/target_date on create/patch → 400 "Dates are disabled for this project".
5. Wiki = project pages, flat. Page.parent writes rejected (400 "Nested pages are disabled"). Pages linkable to tasks via existing page-link mechanism.
6. Two global flat lists: GET /api/work/my/ (assignee = me, all workspaces) and GET /api/work/all/ (everything). Flat rows: id, name, done, state_id, project_id, workspace_slug, assignees. Optional ?done=true|false filter. No grouping.
7. Everything else has no route: cycles, modules, intake, estimates, views, analytics, comments (app + v1 + public space), reactions on comments, draft issues, deploy boards, favorites, stickies, recent visits, importer/exporter, webhooks, integrations. DB tables remain (migration graph untouched), API surface is gone.

## Deletion policy

Routes/serializers/views deleted; Django models kept. Removing models forces a migration-graph reset across 122 migrations for no user-visible gain — a dead route is a dead feature.

## Backend changes (apps/api)

- plane/app/views/workspace/base.py — create() returns 403 before any other logic.
- plane/app/views/project/base.py — no project-count gate (many projects allowed).
- plane/app/views/page/base.py — parent set on create/update → 400.
- plane/db/models/project.py + migration 0123 — calendar_enabled BooleanField default False.
- plane/app/serializers/issue.py — description\_\* read-only on IssueCreateSerializer; validate() rejects dates when project calendar disabled.
- plane/api/serializers/issue.py — description\_\* popped in validate(); same date gate.
- plane/app/views/flat.py + plane/app/urls/flat.py — My Work / All Work endpoints.
- URL unregistrations: cycles, modules, intake, estimates, views, analytics, webhooks, external, exporter, comments (issue.py, api/work_item.py, space/issue.py), comment reactions, issue-dates bulk endpoint, work-item description-versions, draft-issues, deploy-boards, favorites, stickies, recent-visits, quick-links, home-preferences, workspace modules/cycles/estimates lists.

## Verified probes (Django test client + curl, 2026-08-28)

- POST /api/workspaces/ → 403 {"error":"Workspace creation is disabled"}
- POST issue with dates, calendar off → 400 "Dates are disabled for this project" (app + v1)
- PATCH issue description → 204, DB description_html stays "<p></p>"
- POST v1 issue with description_html → 201, stored description empty
- comments / deploy-boards / draft-issues routes → 404
- calendar_enabled True → dates accepted; back to False → rejected again
- GET /api/work/my/ and /api/work/all/ → 200 flat rows

## Frontend (pending)

- Project context drives Board + Documents tabs only.
- Issue detail: no description editor, no comments, no dates unless project calendar_enabled.
- Sidebar: cycles/modules/views/intake entries gone.
- My Work / All Work as two flat lists.

## Run

apps/api: uv venv .venv --python 3.11; uv pip install -p .venv/bin/python -r requirements/local.txt; .env from .env.example with localhost postgres/redis, AMQP_URL=redis://localhost:6379/1, SECRET_KEY set. DJANGO_SETTINGS_MODULE=plane.settings.local manage.py runserver 8080. Probe user probe@local.dev / probepass123, ws probe-ws.

## MS Teams connector (design, 2026-08-29)

Sources: Perplexity threads 20b53e90 (Teams notifications) and 67afbc83 (SAML SSO), recovered via deplexity to /tmp/ppx/threads/; Microsoft Learn primaries (tab SSO with Entra, send proactive messages, Graph proactive bot install, activity feed notifications, tab configuration page).

Facts.

1. Plane ships no Teams integration. Slack is the only first-party comms app and this fork's apps/api contains no Slack connector source (only the slack_sdk dependency), so the Teams connector is a new module — nothing to rewrite.
2. The strip unregistered webhook and integration routes; the Django models remain. The event source for Teams is the workspace webhook re-enabled (smaller diff than a new emitter).
3. Plane webhooks: publicly reachable https URLs only, v2 event JSON, plane*wh*... secret from CSV, any 2xx = success, 5xx retried with backoff, disabled after 5 failures. Teams Workflow/connector endpoints do not accept the raw v2 shape — a relay normalizes.
4. Tab SSO: TeamsJS app.initialize + authentication.getAuthToken gives an Entra token with silent consent; manifest needs webApplicationInfo with Application ID URI api://<tab-host>/<client-id>. Backend validates oid, tid, preferred_username.
5. Login cannot run inside an iframe. The tab host performs the SSO exchange; the Plane session comes from OIDC against the same tenant. Plane SAML alternative (thread 67afbc83): non-gallery Entra enterprise app, Name ID format email from user.mail, plus claims email / firstName / lastName with EMPTY namespace.
6. Proactive DMs need a stored conversationReference per employee. Obtained on first personal-app open, or via Graph: POST /users/{user-id}/teamwork/installedApps. Cannot DM arbitrary directory users without install.
7. Graph sendActivityFeedNotifications is the bell-icon alternative; DM pings already cover the requirement, feed stays optional.

Shape: one custom Teams app, three surfaces.

1. Configurable tab "Board" (team/channel scope) — iframe of that project's kanban: https://<plane>/{workspaceSlug}/projects/{projectId}/issues/?layout=kanban
2. Configurable tab "Notes" (team/channel scope) — iframe of that project's pages: https://<plane>/{workspaceSlug}/projects/{projectId}/pages/
3. Bot with personal scope — employee DMs.

Mappings.

1. Tab configuration page stores {workspaceSlug, projectId, teamId, channelId} in entityId; the relay keeps projectId → channelId.
2. Personal app first open stores {oid, email, conversationReference}; email (Entra UPN, from OIDC userinfo) is the join key to the Plane user.

Event path (one-way).

1. Plane webhook (routes re-enabled) → relay service (small HTTP receiver) → two sinks.
2. Channel sink: project-shared events (created, state change, urgent, done) → Adaptive Card in the mapped channel with an Open deep link into the Board tab (subEntityId = work item id).
3. Employee sink: assignee added/changed, urgent on an assigned item, due date inside the window, blocked → proactive DM to that user only, card buttons limited to Open Board / Open Item.
4. No reply handling, no thread sync — comments are deleted in this fork, so there is nothing to sync back.

Auth stack.

1. One Entra app registration shared by tab SSO and the Bot Framework channel registration.
2. Plane OIDC client configured in God Mode against that tenant; SAML fallback per item 5 above.
3. This fork controls its own deploy, so the proxy sets Content-Security-Policy frame-ancestors for teams.microsoft.com and the Plane session cookie to SameSite=None; without both, the iframes render blank.

Build order.

1. Re-enable workspace webhook routes in the fork.
2. Entra app registration + Teams manifest (configurableTabs ×2, bots, webApplicationInfo, validDomains = tab host + plane host).
3. Plane OIDC to the tenant; verify the email join end-to-end.
4. Proxy CSP + cookie change.
5. Tab configuration page: pick workspace + project, save entityId.
6. Relay service: receive webhook, verify plane*wh* signature, normalize, post channel card, send DM ping.
7. Employee onboarding: personal app install per user (manual or Graph proactive install), conversationReference stored.

Relay implementation (2026-08-29, build order step 6 done in-process).

1. The relay lives inside the Plane API, no separate service: POST /api/teams/relay/ (TeamsRelayEndpoint) receives the workspace webhook delivery, recomputes HMAC-SHA256 over the raw body with the webhook row's secret_key, compares against X-Plane-Signature via compare_digest, 404 unknown webhook / 403 bad signature.
2. Bodies match by construction: webhook_send_task signs json.dumps(payload) and requests json=payload re-serializes with the same defaults, so the signed bytes are the delivered bytes.
3. Sinks in plane/services/relay_cards.py: channel_sink resolves projectId → TeamsChannelBinding, resolves a channel conversation id once via Bot Framework POST /v3/conversations (cached on the row), posts a MessageCard with Open board action; dm_sink resolves assignee emails → TeamsEmployee rows with stored conversationReference, DMs each. Bot token = client_credentials against login.microsoftonline.com/botframework.com, cached in-process until 60s before expiry. Outbound calls go through pinned_fetch.
4. Tables (migration 0124): teams_channel_bindings (project unique while active; team/channel/tenant/service_url/conversation_id) and teams_employees (binding+email unique while active; oid, conversationReference JSON, optional user FK — email is the join key to Plane users).
5. Admin surface: GET/POST /api/workspaces/<slug>/teams/bindings/ and .../teams/employees/ (workspace-admin permission), plus DELETE binding by id.
6. Tab config page (deploy/teams/config.html) now also POSTs the binding (project_id, team_id, channel_id, tenant_id from TeamsJS context) on save; failure only shows a warning, tab save itself is unaffected. CSRF is not an obstacle: BaseSessionAuthentication.enforce_csrf is a no-op in this fork.
7. Env: MS_APP_ID, MS_APP_PASSWORD, MS_BOT_SERVICE_URL (default https://smba.trafficmanager.net/teams/). Until the Entra app exists the sinks return "bot not configured" and the relay still answers 200.
8. Verified locally: py_compile all new files, makemigrations --check reports no drift after verbose_name fix ("Last Modified By"), manage.py check clean, reverse() resolves all three URL names.
9. Verified live (2026-08-29, deploy a0b5af8d): migration 0124 applied; signed POST with the webhook's plane_wh_ secret → 200 with sink report {"channel":"bot not configured","dm":"bot not configured"}; tampered signature → 403; WebhookSerializer._validate_webhook_url accepts the app's own host (WEBHOOK_ALLOWED_HOSTS=plane-production-a21c.up.railway.app set in Railway env — required, the loop-back guard auto-disallows the request host otherwise); probe webhook/project/binding rows deleted after the test, webhook row kept.

Open items.

1. MS_APP_ID / MS_APP_PASSWORD (bot Entra app) not yet set — until then both sinks answer "bot not configured".
2. Distribution inside the tenant: sideload during build, org-wide app policy for the 4-office rollout.
3. Activity feed notifications — keep as v2 if DM noise needs a quieter channel.
