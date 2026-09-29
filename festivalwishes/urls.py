from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path("admin/", admin.site.urls),

    # Public Festival Wishes website
    path("", include("wishes.urls")),

    # Private Dashboard
    path(
        "my-dashboard/",
        include("dashboard.urls")
    ),
]


# Serve uploaded media files
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
