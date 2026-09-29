from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [

    # =========================
    # AUTH
    # =========================

   path(

        "signup/",

        views.admin_signup,

        name="signup"

    ),


    path(

        "login/",

        views.admin_login,

        name="login"

    ),


    path(

        "logout/",

        views.logout_view,

        name="logout"

    ),



# -----------------------------------------
    # PASSWORD RESET
    # -----------------------------------------

    path(
        "forgot-password/",
        views.forgot_password,
        name="forgot_password"
    ),

    path(
        "reset-password/<uuid:token>/",
        views.reset_password,
        name="reset_password"
    ),

    
    # =========================
    # DASHBOARD
    # =========================

    path("", views.dashboard_home, name="home"),


    # =========================
    # FESTIVALS
    # =========================

    path(
        "festivals/",
        views.festival_list,
        name="festival_list"
    ),

    path(
        "festivals/create/",
        views.festival_create,
        name="festival_create"
    ),

    path(
        "festivals/edit/<int:festival_id>/",
        views.festival_edit,
        name="festival_edit"
    ),

    path(
        "festivals/delete/<int:festival_id>/",
        views.festival_delete,
        name="festival_delete"
    ),


  
  # =====================================================
    # WISH LINK MANAGEMENT
    # =====================================================

    path(
        "wishes/",
        views.wish_list,
        name="wish_list"
    ),

    path(
        "wishes/<int:wish_id>/",
        views.wish_detail,
        name="wish_detail"
    ),

    path(
        "wishes/<int:wish_id>/toggle-status/",
        views.wish_toggle_status,
        name="wish_toggle_status"
    ),

    path(
        "wishes/<int:wish_id>/delete/",
        views.wish_delete,
        name="wish_delete"
    ),


     path(
        "profile/",
        views.admin_profile,
        name="admin_profile"
    ),

    path(
        "profile/update/",
        views.update_admin_profile,
        name="update_admin_profile"
    ),

    path(
        "profile/change-password/",
        views.change_admin_password,
        name="change_admin_password"
    ),


   

    path(
    "record-share/<uuid:wish_token>/",
    views.record_share,
    name="record_share"
),


  # SINGLE ACTIVATE / DEACTIVATE

    path(
        "festivals/<int:festival_id>/toggle-status/",
        views.festival_toggle_status,
        name="festival_toggle_status"
    ),


    # BULK ACTION

    path(
        "festivals/bulk-action/",
        views.festival_bulk_action,
        name="festival_bulk_action"
    ),


path(
    "calendar/",
    views.calendar_home,
    name="calendar"
),

path(
    "calendar/add-reminder/",
    views.calendar_add_reminder,
    name="calendar_add_reminder"
),

path(
    "calendar/reminder/<int:reminder_id>/toggle/",
    views.calendar_toggle_reminder,
    name="calendar_toggle_reminder"
),

path(
    "calendar/reminder/<int:reminder_id>/delete/",
    views.calendar_delete_reminder,
    name="calendar_delete_reminder"
),




]