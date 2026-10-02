from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve
from django.urls import re_path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("wishes.urls")),

    path("my-dashboard/", include("dashboard.urls")),

    path(
    "robots.txt",
    TemplateView.as_view(
        template_name="robots.txt",
        content_type="text/plain"
    ),
),
]


# Serve uploaded media files
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {
            "document_root": settings.MEDIA_ROOT,
        },
    ),
]
