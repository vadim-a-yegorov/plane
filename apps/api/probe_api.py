
import json
from django.test import Client
from plane.db.models import User, Issue, Project

u = User.objects.get(email="probe@local.dev")
c = Client()
c.force_login(u)

def req(method, path, data=None):
    fn = getattr(c, method.lower())
    r = fn(path, data=json.dumps(data), content_type="application/json") if data is not None else fn(path)
    body = r.content[:220].decode(errors="replace")
    print(method, path, "->", r.status_code, body.replace("\n", " ")[:200])
    return r

req("post", "/api/workspaces/", {"name": "X", "slug": "x-ws"})
req("post", "/api/workspaces/probe-ws/projects/63f14813-d6eb-46e1-8414-cc667b5a547c/issues/", {"name": "date probe", "start_date": "2026-09-01", "target_date": "2026-09-02"})
r = req("post", "/api/workspaces/probe-ws/projects/63f14813-d6eb-46e1-8414-cc667b5a547c/issues/", {"name": "desc probe", "description_html": "<p>hidden</p>"})
req("get", "/api/work/my/")
req("get", "/api/work/all/")
req("patch", "/api/workspaces/probe-ws/projects/63f14813-d6eb-46e1-8414-cc667b5a547c/issues/a8fe9b6b-f946-4e19-a21f-7876d5361f4b/", {"description_html": "<p>sneak</p>"})
print("DB desc after patch:", repr(Issue.objects.get(id="a8fe9b6b-f946-4e19-a21f-7876d5361f4b").description_html))

req("patch", "/api/workspaces/probe-ws/projects/63f14813-d6eb-46e1-8414-cc667b5a547c/", {"calendar_enabled": True})
r = req("post", "/api/workspaces/probe-ws/projects/63f14813-d6eb-46e1-8414-cc667b5a547c/issues/", {"name": "date ok probe", "start_date": "2026-09-01", "target_date": "2026-09-02"})
req("patch", "/api/workspaces/probe-ws/projects/63f14813-d6eb-46e1-8414-cc667b5a547c/", {"calendar_enabled": False})
print("CAL now:", Project.objects.get(id="63f14813-d6eb-46e1-8414-cc667b5a547c").calendar_enabled)
