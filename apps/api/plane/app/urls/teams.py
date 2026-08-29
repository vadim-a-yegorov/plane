from django.urls import path

from plane.app.views import TeamsBindingEndpoint, TeamsEmployeeEndpoint, TeamsRelayEndpoint

urlpatterns = [
    path("teams/relay/", TeamsRelayEndpoint.as_view(), name="teams-relay"),
    path("workspaces/<str:slug>/teams/bindings/", TeamsBindingEndpoint.as_view(), name="teams-bindings"),
    path("workspaces/<str:slug>/teams/bindings/<uuid:pk>/", TeamsBindingEndpoint.as_view(), name="teams-binding"),
    path("workspaces/<str:slug>/teams/employees/", TeamsEmployeeEndpoint.as_view(), name="teams-employees"),
]
