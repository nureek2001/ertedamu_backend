from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "min_months",
        "max_months",
        "is_active",
        "order",
    )
    list_filter = ("category", "is_active")
    search_fields = ("title", "tag", "content")