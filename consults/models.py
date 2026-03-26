from django.db import models


class Doctor(models.Model):
    CATEGORY_CHOICES = [
        ("pediatric", "Педиатрия"),
        ("neuro", "Невролог"),
        ("speech", "Логопед"),
        ("psych", "Психолог"),
        ("ortho", "Ортопед"),
    ]

    name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    image = models.URLField()
    color = models.CharField(max_length=20, default="#6366F1")
    min_age = models.PositiveIntegerField(default=0)
    max_age = models.PositiveIntegerField(default=180)
    online = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-id"]

    def __str__(self):
        return self.name


class ConsultationArticle(models.Model):
    title = models.CharField(max_length=255)
    icon = models.CharField(max_length=100, default="book-outline")
    color = models.CharField(max_length=20, default="#6366F1")
    content = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-id"]

    def __str__(self):
        return self.title


class Appointment(models.Model):
    CONSULT_TYPE_CHOICES = [
        ("video", "Видеочат"),
        ("chat", "Чат"),
        ("offline", "Офлайн"),
    ]

    child = models.ForeignKey(
        "families.Child",
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    consult_type = models.CharField(max_length=20, choices=CONSULT_TYPE_CHOICES, default="video")
    note = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["appointment_date", "appointment_time"]

    def __str__(self):
        return f"{self.child.first_name} - {self.doctor.name}"