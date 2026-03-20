from django.core.management.base import BaseCommand
from milestones.models import MilestoneCategory, Milestone


class Command(BaseCommand):
    help = "Создаёт стартовые milestones"

    def handle(self, *args, **options):
        categories = [
            {"name": "Motor", "slug": "motor"},
            {"name": "Speech", "slug": "speech"},
            {"name": "Social", "slug": "social"},
            {"name": "Cognitive", "slug": "cognitive"},
        ]

        for item in categories:
            MilestoneCategory.objects.update_or_create(
                slug=item["slug"],
                defaults={"name": item["name"]}
            )

        milestones_data = [
            {
                "title": "Ходит самостоятельно",
                "description": "Ребёнок может ходить без поддержки.",
                "category_slug": "motor",
                "min_age_months": 10,
                "max_age_months": 18,
            },
            {
                "title": "Произносит простые слова",
                "description": "Ребёнок говорит мама, папа и другие простые слова.",
                "category_slug": "speech",
                "min_age_months": 12,
                "max_age_months": 24,
            },
            {
                "title": "Показывает пальцем на интересующий предмет",
                "description": "Ребёнок использует указательный жест для общения.",
                "category_slug": "social",
                "min_age_months": 10,
                "max_age_months": 20,
            },
            {
                "title": "Следует простой инструкции",
                "description": "Ребёнок понимает и выполняет простые просьбы.",
                "category_slug": "cognitive",
                "min_age_months": 14,
                "max_age_months": 30,
            },
        ]

        created_count = 0
        updated_count = 0

        for item in milestones_data:
            category = MilestoneCategory.objects.get(slug=item["category_slug"])

            _, created = Milestone.objects.update_or_create(
                title=item["title"],
                defaults={
                    "description": item["description"],
                    "category": category,
                    "min_age_months": item["min_age_months"],
                    "max_age_months": item["max_age_months"],
                    "is_active": True,
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Milestones seeded. Created: {created_count}, Updated: {updated_count}"
            )
        )