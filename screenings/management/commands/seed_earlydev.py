from django.core.management.base import BaseCommand
from django.db import transaction

from screenings.models import ScreeningTemplate, ScreeningQuestion


EARLY_DEV_TEMPLATE = {
    "title": "Early Development Screening",
    "code": "early_dev",
    "template_type": "early_dev",
    "description": (
        "Скрининг раннего развития ребёнка по базовым возрастным навыкам: "
        "двигательные, речевые, социальные и когнитивные признаки."
    ),
    "min_age_months": 0,
    "max_age_months": 15,
    "version": "1.0",
    "is_active": True,
    "cooldown_days": 30,
}

# Для early_dev отдельной таблицы вариантов ответов у тебя нет,
# поэтому используем answer_type='yes_no'.
# Ответы потом будут сохраняться в ScreeningAnswer.answer_value: 'yes' / 'no'
EARLY_DEV_QUESTIONS = [
    {
        "order": 1,
        "text": "Ребёнок удерживает взгляд на лице взрослого или ярком предмете?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 2,
        "text": "Ребёнок реагирует на громкий звук или голос?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 3,
        "text": "Ребёнок улыбается в ответ на общение с взрослым?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 4,
        "text": "Ребёнок удерживает голову в соответствии со своим возрастом?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 5,
        "text": "Ребёнок переворачивается, садится или ползает в соответствии со своим возрастом?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 6,
        "text": "Ребёнок пытается тянуться к игрушке и брать предметы руками?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 7,
        "text": "Ребёнок перекладывает предмет из одной руки в другую?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 8,
        "text": "Ребёнок лепечет, произносит звуки или слоги в соответствии со своим возрастом?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 9,
        "text": "Ребёнок откликается на своё имя?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 10,
        "text": "Ребёнок понимает простые обращения или запреты?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 11,
        "text": "Ребёнок показывает интерес к людям и взаимодействию с ними?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 12,
        "text": "Ребёнок играет с игрушками по назначению или пытается исследовать их осмысленно?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 13,
        "text": "Ребёнок пытается вставать, ходить вдоль опоры или ходить самостоятельно в соответствии со своим возрастом?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 14,
        "text": "Ребёнок использует жесты, указательный палец или другие способы, чтобы привлечь внимание взрослого?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
    {
        "order": 15,
        "text": "Ребёнок произносит слова или короткие фразы в соответствии со своим возрастом?",
        "answer_type": "yes_no",
        "risk_answer": "no",
        "is_required": True,
    },
]


class Command(BaseCommand):
    help = "Создаёт шаблон early_dev и вопросы для раннего скрининга развития"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Удалить существующие вопросы early_dev и создать заново",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options["reset"]

        template, created = ScreeningTemplate.objects.update_or_create(
            code=EARLY_DEV_TEMPLATE["code"],
            defaults=EARLY_DEV_TEMPLATE,
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Создан ScreeningTemplate: {template.title} ({template.code})"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Обновлён ScreeningTemplate: {template.title} ({template.code})"
                )
            )

        if reset:
            deleted_count, _ = ScreeningQuestion.objects.filter(template=template).delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Удалено старых вопросов early_dev: {deleted_count}"
                )
            )

        created_count = 0
        updated_count = 0

        for item in EARLY_DEV_QUESTIONS:
            question, q_created = ScreeningQuestion.objects.update_or_create(
                template=template,
                order=item["order"],
                defaults={
                    "text": item["text"],
                    "answer_type": item["answer_type"],
                    "risk_answer": item["risk_answer"],
                    "is_required": item["is_required"],
                },
            )

            if q_created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Создан вопрос #{question.order}: {question.text}"
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Обновлён вопрос #{question.order}: {question.text}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Готово. Template={template.code}, создано вопросов={created_count}, обновлено={updated_count}"
            )
        )
        self.stdout.write(
            "Примечание: для early_dev варианты ответов отдельно не создаются, "
            "так как в модели есть только answer_type='yes_no', а сами ответы "
            "сохраняются в ScreeningAnswer.answer_value."
        )