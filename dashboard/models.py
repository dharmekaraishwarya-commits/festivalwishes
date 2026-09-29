from datetime import timezone
import uuid
from django.db import models
from django.utils import timezone


class AdminUser(models.Model):

    ROLE_CHOICES = [
        ("superadmin", "Super Admin"),
        ("admin", "Admin"),
        ("editor", "Editor"),
    ]

    username = models.CharField(
        max_length=100,
        unique=True
    )

    email = models.EmailField(
        unique=True
    )

    password = models.CharField(
        max_length=255
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="admin"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    last_login = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.username

    @property
    def role_name(self):
        return self.get_role_display()


class PasswordResetToken(models.Model):

    admin_user = models.ForeignKey(
        AdminUser,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens"
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    used = models.BooleanField(
        default=False
    )

    def is_valid(self):

        return (
            not self.used
            and timezone.now() < self.expires_at
        )

    def __str__(self):

        return f"Password reset - {self.admin_user.username}"





from django.db import models


# ============================================================
# FESTIVAL CALENDAR REMINDER
# ============================================================

class CalendarReminder(models.Model):

    festival = models.ForeignKey(
        "wishes.Festival",
        on_delete=models.CASCADE,
        related_name="calendar_reminders"
    )

    REMINDER_CHOICES = [
        (30, "30 days before"),
        (14, "14 days before"),
        (7, "7 days before"),
        (3, "3 days before"),
        (1, "1 day before"),
        (0, "On festival day"),
    ]

    reminder_days = models.PositiveIntegerField(
        choices=REMINDER_CHOICES,
        default=7
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = [
            "reminder_days",
            "festival__date"
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "festival",
                    "reminder_days"
                ],
                name="unique_festival_reminder"
            )
        ]

    def __str__(self):

        if self.reminder_days == 0:

            return (
                f"{self.festival.name} - "
                f"On festival day"
            )

        return (
            f"{self.festival.name} - "
            f"{self.reminder_days} days before"
        )
