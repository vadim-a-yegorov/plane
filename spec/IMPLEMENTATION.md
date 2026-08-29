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
- plane/app/serializers/issue.py — description_* read-only on IssueCreateSerializer; validate() rejects dates when project calendar disabled.
- plane/api/serializers/issue.py — description_* popped in validate(); same date gate.
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
