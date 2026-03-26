from rest_framework import serializers

from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "category",
            "tag",
            "read_time",
            "image",
            "color",
            "min_months",
            "max_months",
            "content",
        ]