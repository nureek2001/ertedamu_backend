from django.core.management.base import BaseCommand
from django.utils.text import slugify
from activities.models import ActivityCategory, Activity


class Command(BaseCommand):
    help = "Создаёт стартовые категории и активности"

    def handle(self, *args, **options):
        categories = [
            {"name": "Motor Skills", "slug": "motor-skills"},
            {"name": "Speech", "slug": "speech"},
            {"name": "Social", "slug": "social"},
            {"name": "Cognitive", "slug": "cognitive"},
        ]

        for item in categories:
            ActivityCategory.objects.update_or_create(
                slug=item["slug"],
                defaults={"name": item["name"]}
            )

        activities_data = [
            {
                "title": "Собирание пирамидки",
                "description": "Ребёнок собирает кольца пирамидки по размеру.",
                "instructions": "Покажите пример и дайте ребёнку повторить.",
                "category_slug": "motor-skills",
                "min_age_months": 12,
                "max_age_months": 24,
                "duration_minutes": 10,
            },
            {
                "title": "Повторение звуков",
                "description": "Ребёнок повторяет простые слоги и звуки.",
                "instructions": "Произносите ма-ма, па-па, ба-ба и просите повторять.",
                "category_slug": "speech",
                "min_age_months": 12,
                "max_age_months": 30,
                "duration_minutes": 10,
            },
            {
                "title": "Игра в ладушки",
                "description": "Развитие социальной реакции и подражания.",
                "instructions": "Играйте вместе и хвалите за участие.",
                "category_slug": "social",
                "min_age_months": 8,
                "max_age_months": 24,
                "duration_minutes": 5,
            },
            {
                "title": "Найди игрушку",
                "description": "Развитие внимания и понимания речи.",
                "instructions": "Попросите ребёнка найти знакомую игрушку среди нескольких.",
                "category_slug": "cognitive",
                "min_age_months": 18,
                "max_age_months": 36,
                "duration_minutes": 10,
            },
        ]

        created_count = 0
        updated_count = 0

        for item in activities_data:
            category = ActivityCategory.objects.get(slug=item["category_slug"])
            slug = slugify(item["title"])

            _, created = Activity.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": item["title"],
                    "description": item["description"],
                    "instructions": item["instructions"],
                    "category": category,
                    "min_age_months": item["min_age_months"],
                    "max_age_months": item["max_age_months"],
                    "duration_minutes": item["duration_minutes"],
                    "is_active": True,
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Activities seeded. Created: {created_count}, Updated: {updated_count}"
            )
        )