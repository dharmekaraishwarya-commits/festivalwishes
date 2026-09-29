# =========================================================
# IMPORTS
# =========================================================

from calendar import calendar
from datetime import date, timedelta

from django.contrib.auth.hashers import (
    make_password,
    check_password
)

from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from django.db.models import Q, Count

from django.http import JsonResponse
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.urls import reverse

from django.utils import timezone

from django.utils.dateparse import parse_datetime

from django.utils.text import slugify
from scipy import stats


from .models import (
    AdminUser,
    CalendarReminder,
    PasswordResetToken
)

from wishes.models import (
    Festival,
    WishLog
)


# =========================================================
# ADMIN SIGNUP
# =========================================================

def admin_signup(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )


        # -----------------------------------------
        # VALIDATION
        # -----------------------------------------

        if not username or not email or not password:

            return render(
                request,
                "dashboard/signup.html",
                {
                    "error":
                    "All fields are required."
                }
            )


        if password != confirm_password:

            return render(
                request,
                "dashboard/signup.html",
                {
                    "error":
                    "Passwords do not match."
                }
            )


        if len(password) < 8:

            return render(
                request,
                "dashboard/signup.html",
                {
                    "error":
                    "Password must contain at least 8 characters."
                }
            )


        # -----------------------------------------
        # USERNAME EXISTS
        # -----------------------------------------

        if AdminUser.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "dashboard/signup.html",
                {
                    "error":
                    "Username already exists."
                }
            )


        # -----------------------------------------
        # EMAIL EXISTS
        # -----------------------------------------

        if AdminUser.objects.filter(
            email__iexact=email
        ).exists():

            return render(
                request,
                "dashboard/signup.html",
                {
                    "error":
                    "Email already exists."
                }
            )


        # -----------------------------------------
        # CREATE ADMIN
        # -----------------------------------------

        AdminUser.objects.create(

            username=username,

            email=email,

            password=make_password(
                password
            )

        )


        # -----------------------------------------
        # TOAST
        # -----------------------------------------

        return redirect(
            f"{reverse('dashboard:login')}?toast=signup"
        )


    return render(
        request,
        "dashboard/signup.html"
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

def admin_login(request):

    # Already logged in
    if request.session.get(
        "dashboard_user_id"
    ):

        return redirect(
            "dashboard:home"
        )


    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        remember_me = request.POST.get(
            "remember_me"
        )


        # -----------------------------------------
        # VALIDATION
        # -----------------------------------------

        if not username or not password:

            return render(
                request,
                "dashboard/login.html",
                {
                    "error":
                    "Please enter username and password."
                }
            )


        # -----------------------------------------
        # FIND ADMIN
        # -----------------------------------------

        try:

            admin_user = AdminUser.objects.get(
                username=username
            )

        except AdminUser.DoesNotExist:

            return render(
                request,
                "dashboard/login.html",
                {
                    "error":
                    "Invalid username or password."
                }
            )


        # -----------------------------------------
        # PASSWORD
        # -----------------------------------------

        if not check_password(
            password,
            admin_user.password
        ):

            return render(
                request,
                "dashboard/login.html",
                {
                    "error":
                    "Invalid username or password."
                }
            )


        # -----------------------------------------
        # CLEAR OLD SESSION
        # -----------------------------------------

        request.session.flush()


        # -----------------------------------------
        # CREATE SESSION
        # -----------------------------------------

        request.session[
            "dashboard_user_id"
        ] = admin_user.id

        request.session[
            "dashboard_username"
        ] = admin_user.username


        # -----------------------------------------
        # REMEMBER ME
        # -----------------------------------------

        if remember_me:

            request.session.set_expiry(
                60 * 60 * 24 * 30
            )

        else:

            request.session.set_expiry(
                0
            )


        # -----------------------------------------
        # LOGIN TOAST
        # -----------------------------------------

        return redirect(
            f"{reverse('dashboard:home')}?toast=login"
        )


    return render(
        request,
        "dashboard/login.html"
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

def logout_view(request):

    request.session.flush()

    return redirect(
        f"{reverse('dashboard:login')}?toast=logout"
    )


# =========================================================
# FORGOT PASSWORD
# =========================================================

def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()


        if not email:

            return render(
                request,
                "dashboard/forgot_password.html",
                {
                    "error":
                    "Please enter your email address."
                }
            )


        try:

            admin_user = AdminUser.objects.get(
                email__iexact=email
            )

        except AdminUser.DoesNotExist:

            return render(
                request,
                "dashboard/forgot_password.html",
                {
                    "success":
                    "If an account exists with this email, "
                    "a password reset link has been sent."
                }
            )


        # -----------------------------------------
        # DELETE OLD TOKENS
        # -----------------------------------------

        PasswordResetToken.objects.filter(
            admin_user=admin_user,
            used=False
        ).delete()


        # -----------------------------------------
        # CREATE TOKEN
        # -----------------------------------------

        reset_token = PasswordResetToken.objects.create(

            admin_user=admin_user,

            expires_at=(
                timezone.now()
                + timedelta(minutes=30)
            )

        )


        # -----------------------------------------
        # RESET URL
        # -----------------------------------------

        reset_url = request.build_absolute_uri(

            reverse(
                "dashboard:reset_password",
                kwargs={
                    "token":
                    reset_token.token
                }
            )

        )


        # -----------------------------------------
        # EMAIL
        # -----------------------------------------

        send_mail(

            subject=
            "Reset Your Festival Wishes Password",

            message=f"""
Hello {admin_user.username},

We received a request to reset your Festival Wishes dashboard password.

Click the link below to create a new password:

{reset_url}

This link will expire in 30 minutes.

If you did not request a password reset, you can safely ignore this email.

Festival Wishes
""",

            from_email=None,

            recipient_list=[
                admin_user.email
            ],

            fail_silently=False

        )


        return render(
            request,
            "dashboard/forgot_password.html",
            {
                "success":
                "Password reset link sent! "
                "Please check your email."
            }
        )


    return render(
        request,
        "dashboard/forgot_password.html"
    )


# =========================================================
# RESET PASSWORD
# =========================================================

def reset_password(
    request,
    token
):

    reset_token = get_object_or_404(
        PasswordResetToken,
        token=token
    )


    # -----------------------------------------
    # CHECK TOKEN
    # -----------------------------------------

    if not reset_token.is_valid():

        return render(
            request,
            "dashboard/reset_password.html",
            {
                "invalid_token":
                True
            }
        )


    # -----------------------------------------
    # POST
    # -----------------------------------------

    if request.method == "POST":

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )


        if len(password) < 8:

            return render(
                request,
                "dashboard/reset_password.html",
                {
                    "error":
                    "Password must contain at least 8 characters.",

                    "token":
                    token
                }
            )


        if password != confirm_password:

            return render(
                request,
                "dashboard/reset_password.html",
                {
                    "error":
                    "Passwords do not match.",

                    "token":
                    token
                }
            )


        # -----------------------------------------
        # UPDATE PASSWORD
        # -----------------------------------------

        admin_user = reset_token.admin_user

        admin_user.password = make_password(
            password
        )

        admin_user.save(
            update_fields=[
                "password"
            ]
        )


        # -----------------------------------------
        # MARK TOKEN USED
        # -----------------------------------------

        reset_token.used = True

        reset_token.save(
            update_fields=[
                "used"
            ]
        )


        # -----------------------------------------
        # SUCCESS TOAST
        # -----------------------------------------

        return redirect(
            f"{reverse('dashboard:login')}?toast=password_changed"
        )


    return render(
        request,
        "dashboard/reset_password.html",
        {
            "token":
            token
        }
    )


# =========================================================
# DASHBOARD HOME
# =========================================================

# def dashboard_home(request):

#     # -----------------------------------------
#     # LOGIN CHECK
#     # -----------------------------------------

#     user_id = request.session.get(
#         "dashboard_user_id"
#     )

#     if not user_id:

#         return redirect(
#             "dashboard:login"
#         )


#     # -----------------------------------------
#     # ADMIN USER
#     # -----------------------------------------

#     try:

#         admin_user = AdminUser.objects.get(
#             id=user_id
#         )

#     except AdminUser.DoesNotExist:

#         request.session.flush()

#         return redirect(
#             "dashboard:login"
#         )


#     # -----------------------------------------
#     # STATISTICS
#     # -----------------------------------------

#     total_festivals = Festival.objects.count()

#     total_wishes = WishLog.objects.count()

#     trending_festivals = Festival.objects.filter(
#         is_trending=True
#     ).count()


#     # IMPORTANT:
#     # Sum views instead of Count("views")

#     total_views = Festival.objects.aggregate(
#         total=Count("views")
#     )["total"] or 0


#     # -----------------------------------------
#     # RECENT WISHES
#     # -----------------------------------------

#     recent_wishes = (

#         WishLog.objects

#         .select_related(
#             "festival"
#         )

#         .order_by(
#             "-created_at"
#         )[:10]

#     )


#     # -----------------------------------------
#     # POPULAR FESTIVALS
#     # -----------------------------------------

#     popular_festivals = (

#         Festival.objects

#         .order_by(
#             "-views"
#         )[:5]

#     )


#     # -----------------------------------------
#     # MOST WISHED FESTIVALS
#     # -----------------------------------------

#     festivals_with_wishes = (

#         Festival.objects

#         .annotate(
#             wish_count=Count("wishes")
#         )

#         .order_by(
#             "-wish_count"
#         )[:5]

#     )


#     # -----------------------------------------
#     # CONTEXT
#     # -----------------------------------------

#     context = {

#         "admin_user":
#         admin_user,

#         "username":
#         admin_user.username,

#         "dashboard_username":
#         admin_user.username,

#         "total_festivals":
#         total_festivals,

#         "total_wishes":
#         total_wishes,

#         "trending_festivals":
#         trending_festivals,

#         "total_views":
#         total_views,

#         "recent_wishes":
#         recent_wishes,

#         "popular_festivals":
#         popular_festivals,

#         "festivals_with_wishes":
#         festivals_with_wishes,

#     }


#     return render(
#         request,
#         "dashboard/index.html",
#         context
#     )



from django.shortcuts import render, redirect
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta



# def dashboard_home(request):

#     # =====================================================
#     # CHECK LOGIN
#     # =====================================================

#     user_id = request.session.get("dashboard_user_id")

#     if not user_id:
#         return redirect("dashboard:login")


#     # =====================================================
#     # GET ADMIN USER
#     # =====================================================

#     try:
#         admin_user = AdminUser.objects.get(id=user_id)

#     except AdminUser.DoesNotExist:
#         request.session.flush()
#         return redirect("dashboard:login")


#     # =====================================================
#     # BASIC STATISTICS
#     # =====================================================

#     total_festivals = Festival.objects.count()

#     total_wishes = WishLog.objects.count()

#     trending_festivals = Festival.objects.filter(
#         is_trending=True
#     ).count()

#     popular_festivals = Festival.objects.order_by(
#         "-views"
#     )[:5]


#     # =====================================================
#     # TOTAL VIEWS
#     # =====================================================

#     total_views = Festival.objects.aggregate(
#         total=Count("views")
#     )["total"] or 0


#     # =====================================================
#     # CURRENT TIME
#     # =====================================================

#     now = timezone.localtime()

#     today = now.date()


#     # =====================================================
#     # TODAY
#     # =====================================================

#     today_wishes = WishLog.objects.filter(
#         created_at__date=today
#     ).count()


#     # =====================================================
#     # THIS WEEK
#     # =====================================================

#     week_start = today - timedelta(
#         days=today.weekday()
#     )

#     week_wishes = WishLog.objects.filter(
#         created_at__date__gte=week_start,
#         created_at__date__lte=today
#     ).count()


#     # =====================================================
#     # THIS MONTH
#     # =====================================================

#     month_start = today.replace(
#         day=1
#     )

#     month_wishes = WishLog.objects.filter(
#         created_at__date__gte=month_start,
#         created_at__date__lte=today
#     ).count()


#     # =====================================================
#     # RECENT WISHES
#     # =====================================================

#     recent_wishes = (
#         WishLog.objects
#         .select_related("festival")
#         .order_by("-created_at")[:10]
#     )


#     # =====================================================
#     # FESTIVALS WITH MOST WISHES
#     # =====================================================

#     festivals_with_wishes = (
#         Festival.objects
#         .annotate(
#             wish_count=Count("wishes")
#         )
#         .order_by("-wish_count")[:5]
#     )


#     # =====================================================
#     # CONTEXT
#     # =====================================================

#     context = {

#         # Admin
#         "admin_user": admin_user,
#         "username": admin_user.username,
#         "dashboard_username": admin_user.username,

#         # Main statistics
#         "total_festivals": total_festivals,
#         "total_wishes": total_wishes,
#         "trending_festivals": trending_festivals,
#         "total_views": total_views,

#         # Time statistics
#         "today_wishes": today_wishes,
#         "week_wishes": week_wishes,
#         "month_wishes": month_wishes,

#         # Lists
#         "recent_wishes": recent_wishes,
#         "popular_festivals": popular_festivals,
#         "festivals_with_wishes": festivals_with_wishes,
#     }


#     return render(
#         request,
#         "dashboard/index.html",
#         context
#     )





from datetime import timedelta

from django.db.models import Count, Sum
from django.shortcuts import render, redirect
from django.utils import timezone


def dashboard_home(request):

    # =====================================================
    # LOGIN CHECK
    # =====================================================

    user_id = request.session.get(
        "dashboard_user_id"
    )

    if not user_id:
        return redirect(
            "dashboard:login"
        )


    # =====================================================
    # ADMIN USER
    # =====================================================

    try:

        admin_user = AdminUser.objects.get(
            id=user_id
        )

    except AdminUser.DoesNotExist:

        request.session.flush()

        return redirect(
            "dashboard:login"
        )


    # =====================================================
    # BASIC STATISTICS
    # =====================================================

    total_festivals = Festival.objects.count()

    total_generated_links = WishLog.objects.count()

    total_shares = (
        WishLog.objects.aggregate(
            total=Sum("share_count")
        )["total"] or 0
    )

    trending_festivals = Festival.objects.filter(
        is_trending=True
    ).count()


    # =====================================================
    # TOTAL FESTIVAL VIEWS
    # =====================================================

    total_views = (
        Festival.objects.aggregate(
            total=Sum("views")
        )["total"] or 0
    )

    total_wishes = WishLog.objects.count()
    # =====================================================
    # CURRENT DATE
    # =====================================================

    today = timezone.localdate()


    # =====================================================
    # TODAY'S FESTIVALS
    # =====================================================

    todays_festivals = Festival.objects.filter(
        date=today
    ).order_by("name")


    # =====================================================
    # UPCOMING FESTIVAL
    # =====================================================

    upcoming_festival = (
        Festival.objects
        .filter(
            date__gt=today
        )
        .order_by("date")
        .first()
    )


    # =====================================================
    # TODAY'S WISHES
    # =====================================================

    today_wishes = WishLog.objects.filter(
        created_at__date=today
    ).count()


    # =====================================================
    # THIS WEEK
    # =====================================================

    week_start = (
        today -
        timedelta(
            days=today.weekday()
        )
    )

    week_wishes = WishLog.objects.filter(
        created_at__date__gte=week_start,
        created_at__date__lte=today
    ).count()


    # =====================================================
    # THIS MONTH
    # =====================================================

    month_start = today.replace(
        day=1
    )

    month_wishes = WishLog.objects.filter(
        created_at__date__gte=month_start,
        created_at__date__lte=today
    ).count()


    # =====================================================
    # RECENT ACTIVITY
    # =====================================================

    recent_activity = (
        WishLog.objects
        .select_related("festival")
        .order_by("-created_at")[:10]
    )


    # =====================================================
    # POPULAR FESTIVALS
    # =====================================================

    popular_festivals = (
        Festival.objects
        .order_by("-views")[:5]
    )


    # =====================================================
    # MOST WISHED FESTIVALS
    # =====================================================

    festivals_with_wishes = (
        Festival.objects
        .annotate(
            wish_count=Count("wishes")
        )
        .order_by("-wish_count")[:5]
    )


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        # Admin
        "admin_user": admin_user,
        "username": admin_user.username,
        "dashboard_username": admin_user.username,

        # Statistics
        "total_festivals": total_festivals,
        "total_generated_links": total_generated_links,
        "total_shares": total_shares,
        "trending_festivals": trending_festivals,
        "total_views": total_views,

        # Festival
        "upcoming_festival": upcoming_festival,
        "todays_festivals": todays_festivals,

        # Wish statistics
        "today_wishes": today_wishes,
        "week_wishes": week_wishes,
        "month_wishes": month_wishes,
        "total_wishes": total_wishes,

        # Activity
        "recent_activity": recent_activity,

        # Existing lists
        "popular_festivals": popular_festivals,
        "festivals_with_wishes": festivals_with_wishes,
    }


    return render(
        request,
        "dashboard/index.html",
        context
    )

# =========================================================
# ADMIN PROFILE
# =========================================================

def admin_profile(request):

    user_id = request.session.get(
        "dashboard_user_id"
    )

    if not user_id:

        return redirect(
            "dashboard:login"
        )


    try:

        admin_user = AdminUser.objects.get(
            id=user_id
        )

    except AdminUser.DoesNotExist:

        request.session.flush()

        return redirect(
            "dashboard:login"
        )


    return render(
        request,
        "dashboard/profile.html",
        {
            "admin_user":
            admin_user
        }
    )


def update_admin_profile(request):
    if not request.session.get("dashboard_user_id"):
        return redirect("dashboard:login")

    admin_user = get_object_or_404(
        AdminUser,
        id=request.session["dashboard_user_id"]
    )

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()

        if not username or not email:
            messages.error(request, "Username and email are required.")
            return redirect("dashboard:admin_profile")

        if AdminUser.objects.filter(
            username=username
        ).exclude(id=admin_user.id).exists():

            messages.error(request, "Username already exists.")
            return redirect("dashboard:admin_profile")

        if AdminUser.objects.filter(
            email=email
        ).exclude(id=admin_user.id).exists():

            messages.error(request, "Email already exists.")
            return redirect("dashboard:admin_profile")

        admin_user.username = username
        admin_user.email = email
        admin_user.save()

        request.session["dashboard_username"] = username

        messages.success(
            request,
            "Profile updated successfully! ✨"
        )

    return redirect("dashboard:admin_profile")


def change_admin_password(request):
    if not request.session.get("dashboard_user_id"):
        return redirect("dashboard:login")

    admin_user = get_object_or_404(
        AdminUser,
        id=request.session["dashboard_user_id"]
    )

    if request.method == "POST":

        current_password = request.POST.get("current_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not check_password(
            current_password,
            admin_user.password
        ):
            messages.error(
                request,
                "Current password is incorrect."
            )
            return redirect("dashboard:admin_profile")

        if len(new_password) < 6:
            messages.error(
                request,
                "New password must be at least 6 characters."
            )
            return redirect("dashboard:admin_profile")

        if new_password != confirm_password:
            messages.error(
                request,
                "New passwords do not match."
            )
            return redirect("dashboard:admin_profile")

        admin_user.password = make_password(new_password)
        admin_user.save()

        messages.success(
            request,
            "Password changed successfully! 🔐"
        )

    return redirect("dashboard:admin_profile")

# =========================================================
# FESTIVAL LIST
# =========================================================

from django.shortcuts import render, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone


def festival_list(request):

    # =====================================================
    # LOGIN CHECK
    # =====================================================

    if not request.session.get(
        "dashboard_user_id"
    ):

        return redirect(
            "dashboard:login"
        )


    # =====================================================
    # BASE QUERY
    # =====================================================

    festivals = Festival.objects.annotate(

        wish_count=Count("wishes")

    )


    # =====================================================
    # SEARCH
    # =====================================================

    search = request.GET.get(
        "search",
        ""
    ).strip()


    if search:

        festivals = festivals.filter(

            Q(
                name__icontains=search
            )

            |

            Q(
                slug__icontains=search
            )

        )


    # =====================================================
    # MONTH
    # =====================================================

    month = request.GET.get(
        "month",
        ""
    ).strip()


    if month.isdigit():

        month_number = int(month)


        if 1 <= month_number <= 12:

            festivals = festivals.filter(

                date__month=month_number

            )


    # =====================================================
    # TODAY
    # =====================================================

    today = timezone.localdate()


    # =====================================================
    # DATE FILTER
    # =====================================================

    date_filter = request.GET.get(
        "date_filter",
        ""
    ).strip()


    if date_filter == "today":

        festivals = festivals.filter(

            date__date=today

        )


    elif date_filter == "upcoming":

        festivals = festivals.filter(

            date__date__gt=today

        )


    elif date_filter == "past":

        festivals = festivals.filter(

            date__date__lt=today

        )


    # =====================================================
    # ACTIVE STATUS
    # =====================================================

    status = request.GET.get(
        "status",
        ""
    ).strip()


    if status == "active":

        festivals = festivals.filter(

            is_active=True

        )


    elif status == "inactive":

        festivals = festivals.filter(

            is_active=False

        )


    # =====================================================
    # TRENDING
    # =====================================================

    trending = request.GET.get(
        "trending",
        ""
    ).strip()


    if trending == "trending":

        festivals = festivals.filter(

            is_trending=True

        )


    elif trending == "normal":

        festivals = festivals.filter(

            is_trending=False

        )


    # =====================================================
    # SORT
    # =====================================================

    sort = request.GET.get(
        "sort",
        "date"
    ).strip()


    if sort == "views":

        festivals = festivals.order_by(

            "-views"

        )


    elif sort == "wishes":

        festivals = festivals.order_by(

            "-wish_count"

        )


    elif sort == "name":

        festivals = festivals.order_by(

            "name"

        )


    elif sort == "newest":

        festivals = festivals.order_by(

            "-id"

        )


    else:

        festivals = festivals.order_by(

            "date"

        )


    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(

        festivals,

        6

    )


    page_number = request.GET.get(
        "page"
    )


    page_obj = paginator.get_page(

        page_number

    )


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "festivals": page_obj,

        "page_obj": page_obj,

        "search": search,

        "month": month,

        "date_filter": date_filter,

        "status": status,

        "trending": trending,

        "sort": sort,

        "today": today,

    }


    return render(

        request,

        "dashboard/festival_list.html",

        context

    )


# =========================================================
# BULK FESTIVAL ACTION
# =========================================================

from django.shortcuts import redirect
from django.urls import reverse


def festival_bulk_action(request):


    # =====================================================
    # LOGIN CHECK
    # =====================================================

    if not request.session.get(
        "dashboard_user_id"
    ):

        return redirect(
            "dashboard:login"
        )


    # =====================================================
    # POST ONLY
    # =====================================================

    if request.method != "POST":

        return redirect(
            "dashboard:festival_list"
        )


    # =====================================================
    # FESTIVAL IDS
    # =====================================================

    festival_ids = request.POST.getlist(

        "festival_ids"

    )


    # =====================================================
    # BULK ACTION
    # =====================================================

    action = request.POST.get(

        "bulk_action",

        ""

    )


    # =====================================================
    # NOTHING SELECTED
    # =====================================================

    if not festival_ids:

        return redirect(

            f"{reverse('dashboard:festival_list')}"
            f"?toast=none"

        )


    # =====================================================
    # GET FESTIVALS
    # =====================================================

    festivals = Festival.objects.filter(

        id__in=festival_ids

    )


    # =====================================================
    # ACTIVATE
    # =====================================================

    if action == "activate":

        festivals.update(

            is_active=True

        )


        return redirect(

            f"{reverse('dashboard:festival_list')}"
            f"?toast=activated"

        )


    # =====================================================
    # DEACTIVATE
    # =====================================================

    elif action == "deactivate":

        festivals.update(

            is_active=False

        )


        return redirect(

            f"{reverse('dashboard:festival_list')}"
            f"?toast=deactivated"

        )


    # =====================================================
    # MARK TRENDING
    # =====================================================

    elif action == "trending":

        festivals.update(

            is_trending=True

        )


        return redirect(

            f"{reverse('dashboard:festival_list')}"
            f"?toast=bulk_trending"

        )


    # =====================================================
    # REMOVE TRENDING
    # =====================================================

    elif action == "normal":

        festivals.update(

            is_trending=False

        )


        return redirect(

            f"{reverse('dashboard:festival_list')}"
            f"?toast=bulk_normal"

        )


    # =====================================================
    # DELETE
    # =====================================================

    elif action == "delete":

        festivals.delete()


        return redirect(

            f"{reverse('dashboard:festival_list')}"
            f"?toast=bulk_deleted"

        )


    # =====================================================
    # INVALID ACTION
    # =====================================================

    return redirect(

        f"{reverse('dashboard:festival_list')}"
        f"?toast=none"

    )


# =========================================================
# CREATE FESTIVAL
# =========================================================

def festival_create(request):

    if not request.session.get(
        "dashboard_user_id"
    ):

        return redirect(
            "dashboard:login"
        )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()


        slug = request.POST.get(
            "slug",
            ""
        ).strip()


        # -----------------------------------------
        # NAME
        # -----------------------------------------

        if not name:

            return render(
                request,
                "dashboard/festival_form.html",
                {
                    "error":
                    "Festival name is required.",

                    "form_data":
                    request.POST
                }
            )


        # -----------------------------------------
        # SLUG
        # -----------------------------------------

        if not slug:

            slug = slugify(
                name
            )

        else:

            slug = slugify(
                slug
            )


        # -----------------------------------------
        # DUPLICATE SLUG
        # -----------------------------------------

        if Festival.objects.filter(
            slug=slug
        ).exists():

            return render(
                request,
                "dashboard/festival_form.html",
                {
                    "error":
                    "A festival with this slug already exists.",

                    "form_data":
                    request.POST
                }
            )


        # -----------------------------------------
        # DATE
        # -----------------------------------------

        date_value = request.POST.get(
            "date",
            ""
        )


        festival_date = None


        if date_value:

            try:

                festival_date = parse_datetime(
                    date_value
                )


                if not festival_date:

                    raise ValueError(
                        "Invalid date"
                    )


                if timezone.is_naive(
                    festival_date
                ):

                    festival_date = timezone.make_aware(
                        festival_date
                    )


            except Exception:

                return render(
                    request,
                    "dashboard/festival_form.html",
                    {
                        "error":
                        "Invalid festival date.",

                        "form_data":
                        request.POST
                    }
                )


        # -----------------------------------------
        # CARD IMAGE
        # -----------------------------------------

        card_image = request.FILES.get(
            "card_image"
        )


        if not card_image:

            return render(
                request,
                "dashboard/festival_form.html",
                {
                    "error":
                    "Festival card image is required.",

                    "form_data":
                    request.POST
                }
            )


        # =================================================
        # CREATE
        # =================================================

        Festival.objects.create(

            name=name,

            slug=slug,

            date=festival_date,

            heading=request.POST.get(
                "heading",
                ""
            ).strip(),

            message_1=request.POST.get(
                "message_1",
                ""
            ).strip(),

            message_2=request.POST.get(
                "message_2",
                ""
            ).strip(),

            message_3=request.POST.get(
                "message_3",
                ""
            ).strip(),

            message_4=request.POST.get(
                "message_4",
                ""
            ).strip(),

            theme_color=request.POST.get(
                "theme_color",
                "#ff9800"
            ).strip(),

            animation=request.POST.get(
                "animation",
                "confetti"
            ),

            is_trending=(
                request.POST.get(
                    "is_trending"
                ) == "on"
            ),

            custom_css=request.POST.get(
                "custom_css",
                ""
            ),

            custom_js=request.POST.get(
                "custom_js",
                ""
            ),

            card_image=card_image,

            background_image=request.FILES.get(
                "background_image"
            ),

            image1=request.FILES.get(
                "image1"
            ),

            image2=request.FILES.get(
                "image2"
            ),

            image3=request.FILES.get(
                "image3"
            ),

            image4=request.FILES.get(
                "image4"
            ),

            image5=request.FILES.get(
                "image5"
            ),

            music=request.FILES.get(
                "music"
            )

        )


        # -----------------------------------------
        # SUCCESS TOAST
        # -----------------------------------------

        return redirect(
            f"{reverse('dashboard:festival_list')}"
            f"?toast=created"
        )


    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "dashboard/festival_form.html"
    )


# =========================================================
# EDIT FESTIVAL
# =========================================================

def festival_edit(
    request,
    festival_id
):

    if not request.session.get(
        "dashboard_user_id"
    ):

        return redirect(
            "dashboard:login"
        )


    festival = get_object_or_404(
        Festival,
        id=festival_id
    )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()


        if not name:

            return render(
                request,
                "dashboard/festival_form.html",
                {
                    "festival":
                    festival,

                    "edit_mode":
                    True,

                    "error":
                    "Festival name is required."
                }
            )


        # -----------------------------------------
        # SLUG
        # -----------------------------------------

        slug = request.POST.get(
            "slug",
            ""
        ).strip()


        if not slug:

            slug = slugify(
                name
            )

        else:

            slug = slugify(
                slug
            )


        # -----------------------------------------
        # DUPLICATE SLUG
        # -----------------------------------------

        if Festival.objects.filter(
            slug=slug
        ).exclude(
            id=festival.id
        ).exists():

            return render(
                request,
                "dashboard/festival_form.html",
                {
                    "festival":
                    festival,

                    "edit_mode":
                    True,

                    "error":
                    "Another festival already uses this slug."
                }
            )


        # -----------------------------------------
        # DATE
        # -----------------------------------------

        date_value = request.POST.get(
            "date",
            ""
        )


        festival_date = None


        if date_value:

            try:

                festival_date = parse_datetime(
                    date_value
                )


                if not festival_date:

                    raise ValueError(
                        "Invalid date"
                    )


                if timezone.is_naive(
                    festival_date
                ):

                    festival_date = timezone.make_aware(
                        festival_date
                    )


            except Exception:

                return render(
                    request,
                    "dashboard/festival_form.html",
                    {
                        "festival":
                        festival,

                        "edit_mode":
                        True,

                        "error":
                        "Invalid festival date."
                    }
                )


        # =================================================
        # UPDATE BASIC DATA
        # =================================================

        festival.name = name

        festival.slug = slug

        festival.date = festival_date

        festival.heading = request.POST.get(
            "heading",
            ""
        ).strip()

        festival.message_1 = request.POST.get(
            "message_1",
            ""
        ).strip()

        festival.message_2 = request.POST.get(
            "message_2",
            ""
        ).strip()

        festival.message_3 = request.POST.get(
            "message_3",
            ""
        ).strip()

        festival.message_4 = request.POST.get(
            "message_4",
            ""
        ).strip()

        festival.theme_color = request.POST.get(
            "theme_color",
            "#ff9800"
        ).strip()

        festival.animation = request.POST.get(
            "animation",
            "confetti"
        )

        festival.is_trending = (
            request.POST.get(
                "is_trending"
            ) == "on"
        )

        festival.custom_css = request.POST.get(
            "custom_css",
            ""
        )

        festival.custom_js = request.POST.get(
            "custom_js",
            ""
        )


        # =================================================
        # IMAGES
        # =================================================

        image_fields = [

            "card_image",

            "background_image",

            "image1",

            "image2",

            "image3",

            "image4",

            "image5",

        ]


        for field in image_fields:

            uploaded_file = request.FILES.get(
                field
            )


            if uploaded_file:

                setattr(
                    festival,
                    field,
                    uploaded_file
                )


        # =================================================
        # MUSIC
        # =================================================

        music = request.FILES.get(
            "music"
        )


        if music:

            festival.music = music


        # =================================================
        # SAVE
        # =================================================

        festival.save()


        # -----------------------------------------
        # SUCCESS TOAST
        # -----------------------------------------

        return redirect(
            f"{reverse('dashboard:festival_list')}"
            f"?toast=updated"
        )


    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "dashboard/festival_form.html",
        {
            "festival":
            festival,

            "edit_mode":
            True
        }
    )


# =========================================================
# DELETE FESTIVAL
# =========================================================

def festival_delete(
    request,
    festival_id
):

    if not request.session.get(
        "dashboard_user_id"
    ):

        return redirect(
            "dashboard:login"
        )


    festival = get_object_or_404(
        Festival,
        id=festival_id
    )


    if request.method == "POST":

        festival.delete()

        return redirect(
            f"{reverse('dashboard:festival_list')}"
            f"?toast=deleted"
        )


    return redirect(
        "dashboard:festival_list"
    )


# =========================================================
# WISH LIST
# =========================================================

from django.db.models import Q

from django.core.paginator import Paginator

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.utils import timezone

from django.http import JsonResponse

from django.urls import reverse


# =========================================================
# WISH LIST
# =========================================================

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone


# =========================================================
# WISH LIST
# =========================================================

def wish_list(request):

    # =====================================================
    # LOGIN CHECK
    # =====================================================

    if not request.session.get("dashboard_user_id"):
        return redirect("dashboard:login")


    # =====================================================
    # CURRENT TIME
    # =====================================================

    now = timezone.now()


    # =====================================================
    # BASE QUERY
    # =====================================================

    wishes = (
        WishLog.objects
        .select_related("festival")
        .all()
    )


    # =====================================================
    # SEARCH
    # =====================================================

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        wishes = wishes.filter(

            Q(sender_name__icontains=search)

            |

            Q(receiver_name__icontains=search)

            |

            Q(wish_token__icontains=search)

            |

            Q(festival__name__icontains=search)

            |

            Q(festival__slug__icontains=search)

        )


    # =====================================================
    # FESTIVAL FILTER
    # =====================================================

    selected_festival = request.GET.get(
        "festival",
        ""
    ).strip()

    if selected_festival:

        try:

            festival_id = int(
                selected_festival
            )

            wishes = wishes.filter(
                festival_id=festival_id
            )

        except (ValueError, TypeError):

            selected_festival = ""


    # =====================================================
    # STATUS FILTER
    # =====================================================

    status = request.GET.get(
        "status",
        ""
    ).strip()


    # ACTIVE
    #
    # Active means:
    # is_active = True
    #
    # AND
    #
    # either no expiration
    # OR expiration has not passed.
    # =====================================================

    if status == "active":

        wishes = wishes.filter(
            is_active=True
        ).filter(

            Q(expires_at__isnull=True)

            |

            Q(expires_at__gte=now)

        )


    # =====================================================
    # INACTIVE
    # =====================================================

    elif status == "inactive":

        wishes = wishes.filter(
            is_active=False
        )


    # =====================================================
    # EXPIRED
    # =====================================================

    elif status == "expired":

        wishes = wishes.filter(
            expires_at__isnull=False,
            expires_at__lt=now
        )


    # =====================================================
    # SORT
    # =====================================================

    sort = request.GET.get(
        "sort",
        "newest"
    ).strip()


    if sort == "oldest":

        wishes = wishes.order_by(
            "created_at"
        )


    elif sort == "views":

        wishes = wishes.order_by(
            "-views",
            "-created_at"
        )


    elif sort == "sender":

        wishes = wishes.order_by(
            "sender_name",
            "-created_at"
        )


    elif sort == "festival":

        wishes = wishes.order_by(
            "festival__name",
            "-created_at"
        )


    else:

        # DEFAULT = NEWEST

        wishes = wishes.order_by(
            "-created_at"
        )


    # =====================================================
    # STATISTICS
    # =====================================================

    # All generated links
    total_wishes = WishLog.objects.count()


    # Active links
    active_wishes = (
        WishLog.objects
        .filter(is_active=True)
        .filter(
            Q(expires_at__isnull=True)
            |
            Q(expires_at__gte=now)
        )
        .count()
    )


    # Expired links
    expired_wishes = (
        WishLog.objects
        .filter(
            expires_at__isnull=False,
            expires_at__lt=now
        )
        .count()
    )


    # Total views
    total_views = (
        WishLog.objects.aggregate(
            total=Sum("views")
        )["total"]
        or 0
    )


    # =====================================================
    # FESTIVALS FOR DROPDOWN
    # =====================================================

    festivals = Festival.objects.order_by(
        "name"
    )


    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        wishes,
        20
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "wishes": page_obj,

        "page_obj": page_obj,

        "festivals": festivals,

        "search": search,

        "selected_festival": selected_festival,

        "status": status,

        "sort": sort,

        "now": now,

        "total_wishes": total_wishes,

        "active_wishes": active_wishes,

        "expired_wishes": expired_wishes,

        "total_views": total_views,

    }


    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "dashboard/wish_detail.html",
        context
    )



@require_POST
def wish_toggle_status(request, wish_id):

    # =====================================================
    # LOGIN CHECK
    # =====================================================

    if not request.session.get(
        "dashboard_user_id"
    ):

        return redirect(
            "dashboard:login"
        )


    # =====================================================
    # GET WISH
    # =====================================================

    wish = get_object_or_404(
        WishLog,
        id=wish_id
    )


    # =====================================================
    # TOGGLE STATUS
    # =====================================================

    wish.is_active = not wish.is_active


    # =====================================================
    # SAVE
    # =====================================================

    wish.save(
        update_fields=[
            "is_active"
        ]
    )


    # =====================================================
    # TOAST
    # =====================================================

    if wish.is_active:

        toast = "wish_enabled"

    else:

        toast = "wish_disabled"


    # =====================================================
    # REDIRECT
    # =====================================================

    return redirect(
        f"{reverse('dashboard:wish_list')}?toast={toast}"
    )



@require_POST
def wish_delete(request, wish_id):

    # =====================================================
    # LOGIN CHECK
    # =====================================================

    if not request.session.get(
        "dashboard_user_id"
    ):

        return redirect(
            "dashboard:login"
        )


    # =====================================================
    # GET WISH
    # =====================================================

    wish = get_object_or_404(
        WishLog,
        id=wish_id
    )


    # =====================================================
    # DELETE
    # =====================================================

    wish.delete()


    # =====================================================
    # REDIRECT WITH TOAST
    # =====================================================

    return redirect(
        f"{reverse('dashboard:wish_list')}?toast=wish_deleted"
    )



def wish_detail(request, wish_id):

    # =====================================================
    # LOGIN CHECK
    # =====================================================

    if not request.session.get(
        "dashboard_user_id"
    ):

        return redirect(
            "dashboard:login"
        )


    # =====================================================
    # GET WISH
    # =====================================================

    wish = get_object_or_404(
        WishLog.objects.select_related(
            "festival"
        ),
        id=wish_id
    )


    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "dashboard/wish_detail.html",
        {
            "wish": wish,
            "now": timezone.now(),
        }
    )
from django.views.decorators.http import require_POST
from django.db.models import F


@require_POST
def record_share(request, wish_token):

    wish = get_object_or_404(
        WishLog,
        wish_token=wish_token
    )

    WishLog.objects.filter(
        id=wish.id
    ).update(
        share_count=F("share_count") + 1
    )

    wish.refresh_from_db()

    return JsonResponse({
        "success": True,
        "share_count": wish.share_count
    })



from django.shortcuts import get_object_or_404
from django.urls import reverse


def festival_toggle_status(
    request,
    festival_id
):


    # =====================================================
    # LOGIN CHECK
    # =====================================================

    if not request.session.get(
        "dashboard_user_id"
    ):

        return redirect(
            "dashboard:login"
        )


    # =====================================================
    # POST ONLY
    # =====================================================

    if request.method != "POST":

        return redirect(
            "dashboard:festival_list"
        )


    # =====================================================
    # GET FESTIVAL
    # =====================================================

    festival = get_object_or_404(

        Festival,

        id=festival_id

    )


    # =====================================================
    # TOGGLE STATUS
    # =====================================================

    if festival.is_active:

        festival.is_active = False

        toast = "deactivated"

    else:

        festival.is_active = True

        toast = "activated"


    # =====================================================
    # SAVE
    # =====================================================

    festival.save(

        update_fields=[
            "is_active"
        ]

    )


    # =====================================================
    # REDIRECT
    # =====================================================

    return redirect(

        f"{reverse('dashboard:festival_list')}"
        f"?toast={toast}"

    )


# ============================================================
# CALENDAR HELPER
# ============================================================

# ============================================================
# IMPORTS
# ============================================================

import calendar as pycalendar

from datetime import date, timedelta

from django.db.models import Q
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.urls import reverse
from django.utils import timezone

from wishes.models import Festival

from .models import CalendarReminder


# ============================================================
# DASHBOARD LOGIN CHECK
# ============================================================

def dashboard_login_required(request):

    """
    Simple session-based dashboard protection.

    This project uses:

        dashboard_user_id

    instead of Django's built-in User authentication.
    """

    return bool(
        request.session.get("dashboard_user_id")
    )


# ============================================================
# CALENDAR HOME
# ============================================================

def calendar_home(request):

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if not dashboard_login_required(request):

        return redirect(
            "dashboard:login"
        )


    # --------------------------------------------------------
    # TODAY
    # --------------------------------------------------------

    today = timezone.localdate()

    tomorrow = today + timedelta(days=1)


    # --------------------------------------------------------
    # SELECTED YEAR
    # --------------------------------------------------------

    try:

        selected_year = int(
            request.GET.get(
                "year",
                today.year
            )
        )

    except (
        ValueError,
        TypeError
    ):

        selected_year = today.year


    # --------------------------------------------------------
    # SELECTED MONTH
    # --------------------------------------------------------

    try:

        selected_month = int(
            request.GET.get(
                "month",
                today.month
            )
        )

    except (
        ValueError,
        TypeError
    ):

        selected_month = today.month


    # --------------------------------------------------------
    # VALIDATE YEAR
    # --------------------------------------------------------

    if selected_year < 1900 or selected_year > 2100:

        selected_year = today.year


    # --------------------------------------------------------
    # VALIDATE MONTH
    # --------------------------------------------------------

    if selected_month < 1 or selected_month > 12:

        selected_month = today.month


    # ========================================================
    # CURRENT MONTH RANGE
    # ========================================================

    first_day = date(
        selected_year,
        selected_month,
        1
    )

    last_day_number = pycalendar.monthrange(
        selected_year,
        selected_month
    )[1]

    last_day = date(
        selected_year,
        selected_month,
        last_day_number
    )


    # ========================================================
    # MONTH FESTIVALS
    # ========================================================

    month_festivals = Festival.objects.filter(

        date__date__gte=first_day,

        date__date__lte=last_day

    ).order_by(
        "date"
    )


    # ========================================================
    # FESTIVAL DATE MAP
    # ========================================================

    festival_map = {}


    for festival in month_festivals:

        festival_date = timezone.localtime(
            festival.date
        ).date()


        if festival_date not in festival_map:

            festival_map[
                festival_date
            ] = []


        festival_map[
            festival_date
        ].append(
            festival
        )


    # ========================================================
    # BUILD CALENDAR
    # ========================================================

    cal = pycalendar.Calendar(
        firstweekday=0
    )

    raw_weeks = cal.monthdatescalendar(
        selected_year,
        selected_month
    )


    calendar_weeks = []


    for week in raw_weeks:

        week_days = []


        for day in week:

            day_data = {

                "date": day,

                "day": day.day,

                "is_current_month":
                    day.month == selected_month,

                "is_today":
                    day == today,

                "festivals":
                    festival_map.get(
                        day,
                        []
                    ),

            }


            week_days.append(
                day_data
            )


        calendar_weeks.append(
            week_days
        )


    # ========================================================
    # PREVIOUS MONTH
    # ========================================================

    if selected_month == 1:

        previous_month = 12
        previous_year = selected_year - 1

    else:

        previous_month = selected_month - 1
        previous_year = selected_year


    # ========================================================
    # NEXT MONTH
    # ========================================================

    if selected_month == 12:

        next_month = 1
        next_year = selected_year + 1

    else:

        next_month = selected_month + 1
        next_year = selected_year


    # ========================================================
    # TODAY'S FESTIVALS
    # ========================================================

    todays_festivals = Festival.objects.filter(

        date__date=today

    ).order_by(
        "date"
    )


    # ========================================================
    # TOMORROW'S FESTIVALS
    # ========================================================

    tomorrows_festivals = Festival.objects.filter(

        date__date=tomorrow

    ).order_by(
        "date"
    )


    # ========================================================
    # THIS WEEK
    # ========================================================

    # Monday = start of week
    week_start = today - timedelta(
        days=today.weekday()
    )

    week_end = week_start + timedelta(
        days=6
    )


    this_week_festivals = Festival.objects.filter(

        date__date__gte=week_start,

        date__date__lte=week_end

    ).order_by(
        "date"
    )


    # ========================================================
    # THIS MONTH
    # ========================================================

    month_start = today.replace(
        day=1
    )

    month_end_number = pycalendar.monthrange(
        today.year,
        today.month
    )[1]

    month_end = today.replace(
        day=month_end_number
    )


    this_month_festivals = Festival.objects.filter(

        date__date__gte=month_start,

        date__date__lte=month_end

    ).order_by(
        "date"
    )


    # ========================================================
    # UPCOMING FESTIVALS
    # ========================================================

    upcoming_festivals = Festival.objects.filter(

        date__date__gte=today

    ).order_by(
        "date"
    )[:12]


    # ========================================================
    # NEXT FESTIVAL
    # ========================================================

    next_festival = Festival.objects.filter(

        date__gte=timezone.now()

    ).order_by(
        "date"
    ).first()


    # ========================================================
    # YEARLY FESTIVALS
    # ========================================================

    yearly_festivals = Festival.objects.filter(

        date__year=selected_year

    ).order_by(
        "date"
    )


    # ========================================================
    # GROUP YEARLY FESTIVALS BY MONTH
    # ========================================================

    yearly_by_month = {

        month_number: []

        for month_number
        in range(1, 13)

    }


    for festival in yearly_festivals:

        festival_month = timezone.localtime(
            festival.date
        ).month


        yearly_by_month[
            festival_month
        ].append(
            festival
        )


    # ========================================================
    # REMINDERS
    # ========================================================

    reminders = CalendarReminder.objects.select_related(
        "festival"
    ).order_by(
        "reminder_days",
        "festival__date"
    )


    # ========================================================
    # MONTH LIST
    # ========================================================

    months_list = [

        (
            month_number,

            pycalendar.month_name[
                month_number
            ]

        )

        for month_number
        in range(1, 13)

    ]


    # ========================================================
    # YEAR DROPDOWN
    # ========================================================

    years = range(

        today.year - 2,

        today.year + 5

    )


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        # Date
        "today":
            today,

        "tomorrow":
            tomorrow,


        # Selected calendar
        "selected_year":
            selected_year,

        "selected_month":
            selected_month,

        "month_name":
            pycalendar.month_name[
                selected_month
            ],


        # Calendar
        "calendar_weeks":
            calendar_weeks,

        "month_festivals":
            month_festivals,


        # Navigation
        "previous_month":
            previous_month,

        "previous_year":
            previous_year,

        "next_month":
            next_month,

        "next_year":
            next_year,


        # Quick cards
        "todays_festivals":
            todays_festivals,

        "tomorrows_festivals":
            tomorrows_festivals,

        "this_week_festivals":
            this_week_festivals,

        "this_month_festivals":
            this_month_festivals,


        # Upcoming
        "upcoming_festivals":
            upcoming_festivals,

        "next_festival":
            next_festival,


        # Year
        "yearly_festivals":
            yearly_festivals,

        "yearly_by_month":
            yearly_by_month,

        "months_list":
            months_list,

        "years":
            years,


        # Reminders
        "reminders":
            reminders,

    }


    return render(

        request,

        "dashboard/calendar/calendar_home.html",

        context

    )


# ============================================================
# ADD REMINDER
# ============================================================

def calendar_add_reminder(request):

    if not dashboard_login_required(request):

        return redirect(
            "dashboard:login"
        )


    if request.method != "POST":

        return redirect(
            "dashboard:calendar"
        )


    festival_id = request.POST.get(
        "festival"
    )

    reminder_days = request.POST.get(
        "reminder_days"
    )


    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    if not festival_id or not reminder_days:

        return redirect(
            f"{reverse('dashboard:calendar')}"
            f"?toast=reminder_error"
        )


    festival = get_object_or_404(

        Festival,

        id=festival_id

    )


    # --------------------------------------------------------
    # INTEGER VALIDATION
    # --------------------------------------------------------

    try:

        reminder_days = int(
            reminder_days
        )

    except (
        ValueError,
        TypeError
    ):

        return redirect(
            f"{reverse('dashboard:calendar')}"
            f"?toast=reminder_error"
        )


    # --------------------------------------------------------
    # ALLOWED VALUES
    # --------------------------------------------------------

    allowed_days = [
        30,
        14,
        7,
        3,
        1,
        0
    ]


    if reminder_days not in allowed_days:

        return redirect(
            f"{reverse('dashboard:calendar')}"
            f"?toast=reminder_error"
        )


    # --------------------------------------------------------
    # CREATE / REACTIVATE
    # --------------------------------------------------------

    CalendarReminder.objects.update_or_create(

        festival=festival,

        reminder_days=reminder_days,

        defaults={
            "is_active": True
        }

    )


    return redirect(

        f"{reverse('dashboard:calendar')}"
        f"?toast=reminder_added"

    )


# ============================================================
# TOGGLE REMINDER
# ============================================================

def calendar_toggle_reminder(
    request,
    reminder_id
):

    if not dashboard_login_required(request):

        return redirect(
            "dashboard:login"
        )


    reminder = get_object_or_404(

        CalendarReminder,

        id=reminder_id

    )


    reminder.is_active = (
        not reminder.is_active
    )


    reminder.save(
        update_fields=[
            "is_active"
        ]
    )


    if reminder.is_active:

        toast = "reminder_enabled"

    else:

        toast = "reminder_disabled"


    return redirect(

        f"{reverse('dashboard:calendar')}"
        f"?toast={toast}"

    )


# ============================================================
# DELETE REMINDER
# ============================================================

def calendar_delete_reminder(
    request,
    reminder_id
):

    if not dashboard_login_required(request):

        return redirect(
            "dashboard:login"
        )


    reminder = get_object_or_404(

        CalendarReminder,

        id=reminder_id

    )


    reminder.delete()


    return redirect(

        f"{reverse('dashboard:calendar')}"
        f"?toast=reminder_deleted"

    )




