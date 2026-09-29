import uuid

from django.db import models
from django.utils.text import slugify


from django.contrib.auth.hashers import make_password

class Festival(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    date = models.DateTimeField()
    views = models.PositiveIntegerField(default=0)
    is_trending = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    # Card image (list page)
    card_image = models.ImageField(upload_to='festival/cards/')

    # Wish page content
    heading = models.CharField(max_length=200, blank=True)
    message_1 = models.TextField(blank=True)
    message_2 = models.TextField(blank=True)
    message_3 = models.TextField(blank=True)
    message_4 = models.TextField(blank=True)

    # Theme
    theme_color = models.CharField(max_length=20, default="#ff9800")

    # Images (multi)
    image1 = models.ImageField(upload_to='festival/images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='festival/images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='festival/images/', blank=True, null=True)
    image4 = models.ImageField(upload_to='festival/images/', blank=True, null=True)
    image5 = models.ImageField(upload_to='festival/images/', blank=True, null=True)

    # Music
    music = models.FileField(upload_to='festival/music/', blank=True, null=True)

    # Animation
    ANIMATION_CHOICES = [
        ('confetti', 'Confetti'),
        ('glitter', 'Glitter'),
        ('fireworks', 'Fireworks'),
    ]
    animation = models.CharField(max_length=20, choices=ANIMATION_CHOICES, default='confetti')

    custom_css = models.TextField(blank=True)
    custom_js = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
    background_image = models.ImageField(
        upload_to='festival/backgrounds/',
        blank=True,
        null=True
    )





class WishLog(models.Model):
    sender_name = models.CharField(max_length=100)

    festival = models.ForeignKey(
        'Festival',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='wishes'
    )

    # Person receiving the wish
    receiver_name = models.CharField(max_length=100, blank=True)

    # Receiver's photo
    receiver_photo = models.ImageField(
        upload_to='wishes/photos/',
        blank=True,
        null=True
    )

    # Unique link identifier
    wish_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    ai_message = models.TextField(
    blank=True,
    null=True
)


    # NEW
    share_count = models.PositiveIntegerField(
        default=0
    )


     # =====================================================
    # LINK VIEWS
    # =====================================================

    views = models.PositiveIntegerField(
        default=0
    )


    # =====================================================
    # LINK STATUS
    # =====================================================

    is_active = models.BooleanField(
        default=True
    )


    # =====================================================
    # EXPIRY DATE
    # =====================================================

    expires_at = models.DateTimeField(
        blank=True,
        null=True
    )

    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender_name} - {self.festival.name if self.festival else 'Unknown'}"




from django.db import models


class BabyVideoTemplate(models.Model):

    name = models.CharField(
        max_length=100
    )

    image = models.ImageField(
        upload_to="baby_templates/"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class BabyVideo(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    sender_name = models.CharField(
        max_length=100
    )

    receiver_name = models.CharField(
        max_length=100
    )

    festival = models.CharField(
        max_length=100,
        blank=True
    )

    script = models.TextField()

    baby_template = models.ForeignKey(
        BabyVideoTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    video = models.FileField(
        upload_to="generated_baby_videos/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    progress = models.PositiveIntegerField(
        default=0
    )

    current_step = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    error_message = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return (
            f"{self.sender_name} → "
            f"{self.receiver_name}"
        )





