from django.db import models


class Article(models.Model):
    CATEGORY_CHOICES = [
        ("health", "Здоровье"),
        ("psych", "Психология"),
        ("edu", "Развитие"),
        ("food", "Питание"),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    tag = models.CharField(max_length=100)
    read_time = models.CharField(max_length=30, default="5 мин")
    image = models.URLField()
    color = models.CharField(max_length=20, default="#6366F1")
    min_months = models.PositiveIntegerField(default=0)
    max_months = models.PositiveIntegerField(default=72)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self) -> str:
        return self.title