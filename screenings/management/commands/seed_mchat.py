from django.core.management.base import BaseCommand
from screenings.models import ScreeningTemplate, ScreeningQuestion


class Command(BaseCommand):
    help = "Создаёт или обновляет шаблон M-CHAT и его вопросы"

    def handle(self, *args, **options):
        template, created = ScreeningTemplate.objects.get_or_create(
            code='mchat',
            defaults={
                'title': 'M-CHAT Screening',
                'template_type': 'mchat',
                'description': 'Modified Checklist for Autism in Toddlers',
                'min_age_months': 16,
                'max_age_months': 30,
                'version': '1.0',
                'is_active': True,
                'cooldown_days': 30,
            }
        )

        if not created:
            template.title = 'M-CHAT Screening'
            template.template_type = 'mchat'
            template.description = 'Modified Checklist for Autism in Toddlers'
            template.min_age_months = 16
            template.max_age_months = 30
            template.version = '1.0'
            template.is_active = True
            template.cooldown_days = 30
            template.save()

        questions_data = [
            {
                "order": 1,
                "text": "Если вы указываете на предмет в комнате, смотрит ли ребёнок на него?",
                "risk_answer": "no",
            },
            {
                "order": 2,
                "text": "Вы когда-нибудь задумывались, что ребёнок может быть глухим?",
                "risk_answer": "yes",
            },
            {
                "order": 3,
                "text": "Играет ли ребёнок в воображаемые или сюжетно-ролевые игры?",
                "risk_answer": "no",
            },
            {
                "order": 4,
                "text": "Любит ли ребёнок взбираться на предметы?",
                "risk_answer": "no",
            },
            {
                "order": 5,
                "text": "Делает ли ребёнок необычные движения пальцами возле глаз?",
                "risk_answer": "yes",
            },
            {
                "order": 6,
                "text": "Указывает ли ребёнок пальцем, чтобы попросить что-то?",
                "risk_answer": "no",
            },
            {
                "order": 7,
                "text": "Указывает ли ребёнок пальцем, чтобы показать вам что-то интересное?",
                "risk_answer": "no",
            },
            {
                "order": 8,
                "text": "Интересуется ли ребёнок другими детьми?",
                "risk_answer": "no",
            },
            {
                "order": 9,
                "text": "Показывает ли ребёнок вам предметы, чтобы поделиться впечатлением?",
                "risk_answer": "no",
            },
            {
                "order": 10,
                "text": "Откликается ли ребёнок, когда его зовут по имени?",
                "risk_answer": "no",
            },
            {
                "order": 11,
                "text": "Улыбается ли ребёнок в ответ на вашу улыбку?",
                "risk_answer": "no",
            },
            {
                "order": 12,
                "text": "Расстраивается ли ребёнок от обычных бытовых звуков?",
                "risk_answer": "yes",
            },
            {
                "order": 13,
                "text": "Ходит ли ребёнок?",
                "risk_answer": "no",
            },
            {
                "order": 14,
                "text": "Смотрит ли ребёнок вам в глаза во время общения?",
                "risk_answer": "no",
            },
            {
                "order": 15,
                "text": "Пытается ли ребёнок копировать ваши действия?",
                "risk_answer": "no",
            },
            {
                "order": 16,
                "text": "Поворачивает ли ребёнок голову, если вы на что-то смотрите?",
                "risk_answer": "no",
            },
            {
                "order": 17,
                "text": "Пытается ли ребёнок привлечь ваше внимание к своим действиям?",
                "risk_answer": "no",
            },
            {
                "order": 18,
                "text": "Понимает ли ребёнок простые инструкции?",
                "risk_answer": "no",
            },
            {
                "order": 19,
                "text": "Смотрит ли ребёнок на ваше лицо, чтобы понять вашу реакцию?",
                "risk_answer": "no",
            },
            {
                "order": 20,
                "text": "Нравятся ли ребёнку подвижные игры, качание, подбрасывание?",
                "risk_answer": "no",
            },
        ]

        created_count = 0
        updated_count = 0

        for item in questions_data:
            _, was_created = ScreeningQuestion.objects.update_or_create(
                template=template,
                order=item["order"],
                defaults={
                    "text": item["text"],
                    "answer_type": "yes_no",
                    "risk_answer": item["risk_answer"],
                    "is_required": True,
                }
            )

            if was_created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"M-CHAT готов. Template ID={template.id}. "
                f"Создано вопросов: {created_count}, обновлено: {updated_count}"
            )
        )