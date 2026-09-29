from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 🏠 Home
    path('', views.home, name='home'),

    # 📃 Festival list
    path('festivals', views.list_festival, name='list_festival'),

    # 🎯 Generate page
    path('generate/<slug:slug>/', views.generate_page, name='generate_page'),

    # 🔗 Generate link (AJAX)
    path('generate-link/', views.generate_link, name='generate_link'),
   


    # 🎉 Final wish page
    path('wish/<slug:slug>/', views.festival_wish, name='festival_wish'),

    path('search/', views.search_festival, name='search_festival'),


    path(
    'generate-ai-wish/',
    views.generate_ai_wish,
    name='generate_ai_wish'),


 path(
        'festivals/',
        views.festival_calendar,
        name='festival_calendar'
    ),


    path(
    'generate-link/<slug:slug>/',
    views.generate_link_page,
    name='generate_link_page'
),


  path(
        "about/",
        views.about,
        name="about"
    ),

    path(
        "contact/",
        views.contact,
        name="contact"
    ),

    path(
        "privacy-policy/",
        views.privacy_policy,
        name="privacy_policy"
    ),

    path(
        "terms/",
        views.terms,
        name="terms"
    ),

    path(
        "disclaimer/",
        views.disclaimer,
        name="disclaimer"
    ),

# qBTCgac7k56qxU
 # Public festival wish page
    path(
        "festival/<slug:slug>/",
        views.festival_wish,
        name="festival_wish"
    ),

  
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



