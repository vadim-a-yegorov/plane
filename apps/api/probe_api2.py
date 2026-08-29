
import json
from django.test import Client
from plane.db.models import User

u = User.objects.get(email="probe@local.dev")
c = Client()
c.force_login(u)

def req(method, path, data=None):
    fn = getattr(c, method.lower())
    r = fn(path, data=json.dumps(data), content_type="application/json") if data is not None else fn(path)
    print("PROBE", method, path, "->", r.status_code, r.content[:160].decode(errors="replace").replace("\n", " "))

req("post", "/api/workspaces/", {"name": "X", "slug": "x-ws"})
req("post", "/api/workspaces/probe-ws/projects/63f14813-d6eb-46e1-8414-cc667b5a547c/issues/", {"name": "date probe 2", "start_date": "2026-09-01", "target_date": "2026-09-02"})
req("get", "/api/workspaces/probe-ws/projects/63f14813-d6eb-46e1-8414-cc667b5a547c/issues/00000000-0000-0000-0000-000000000000/comments/")
req("post", "/api/workspaces/probe-ws/projects/63f14813-d6eb-46e1-8414-cc667b5a547c/project-deploy-boards/", {})
req("get", "/api/workspaces/probe-ws/draft-issues/")
