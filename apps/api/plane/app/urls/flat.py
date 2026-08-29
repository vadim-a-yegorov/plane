from django.urls import path

from plane.app.views.flat import AllWorkEndpoint, MyWorkEndpoint

urlpatterns = [
    path("work/my/", MyWorkEndpoint.as_view(), name="flat-my-work"),
    path("work/all/", AllWorkEndpoint.as_view(), name="flat-all-work"),
]
