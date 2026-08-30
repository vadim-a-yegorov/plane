
import json
from plane.db.models import User, Workspace, Project, Issue, State, WorkspaceMember, ProjectMember, APIToken

u, _ = User.objects.get_or_create(email="probe@local.dev", defaults={"first_name": "Probe"})
u.set_password("probepass123"); u.is_active = True; u.save()

w, _ = Workspace.objects.get_or_create(slug="probe-ws", defaults={"name": "Probe WS", "owner": u})
WorkspaceMember.objects.get_or_create(workspace=w, member=u, defaults={"role": 20})

p, _ = Project.objects.get_or_create(workspace=w, name="Probe Project", defaults={"identifier": "PRB", "created_by": u})
ProjectMember.objects.get_or_create(project=p, member=u, defaults={"role": 20})

st, _ = State.objects.get_or_create(project=p, name="Todo", defaults={"group": "backlog", "created_by": u})
done, _ = State.objects.get_or_create(project=p, name="Done", defaults={"group": "completed", "created_by": u})

i, _ = Issue.objects.get_or_create(project=p, name="probe task", defaults={"state": st, "created_by": u, "workspace": w})

tok, _ = APIToken.objects.get_or_create(user=u, label="probe")
print("TOKEN", tok.token)
print("WS", w.slug, "PROJ", str(p.id), "ISSUE", str(i.id), "STATE", str(st.id), "CAL", p.calendar_enabled)
