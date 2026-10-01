from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # Django Admin
    path(
        "admin/",
        admin.site.urls
    ),

    # Main Festival Wishes Website
    path(
        "",
        include("wishes.urls")
    ),

    # Custom Dashboard
    path(
        "my-dashboard/",
        include("dashboard.urls")
    ),
]


# ============================================================
# MEDIA FILES
# ============================================================
#
# Serve uploaded images:
#
# /media/festival/cards/...
# /media/festival/backgrounds/...
#
# This is enabled even when DEBUG=False so that
# the deployed Render site can access uploaded media.
#
# ============================================================

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
