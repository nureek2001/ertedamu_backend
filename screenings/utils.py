from datetime import timedelta
from django.utils import timezone

from families.utils import calculate_age_months
from .models import ScreeningSession


def is_template_allowed_for_child(template, child):
    age_months = calculate_age_months(child.birth_date)
    return template.min_age_months <= age_months <= template.max_age_months


def get_last_completed_session(child, template):
    return ScreeningSession.objects.filter(
        child=child,
        template=template,
        status='completed'
    ).order_by('-completed_at').first()


def can_start_screening(child, template):
    if not is_template_allowed_for_child(template, child):
        return False, "Возраст ребёнка не подходит для данного скрининга."

    last_session = get_last_completed_session(child, template)
    if not last_session:
        return True, None

    next_allowed_date = last_session.completed_at + timedelta(days=template.cooldown_days)
    if timezone.now() < next_allowed_date:
        return False, f"Следующее прохождение доступно после {next_allowed_date.date()}."

    return True, None


def calculate_mchat_result(session):
    """
    Для M-CHAT:
    риск = количество ответов, совпавших с risk_answer у вопроса.
    low: 0-2
    medium: 3-7
    high: 8+
    """
    score = 0
    answers = session.answers.select_related('question').all()

    for answer in answers:
        risk_answer = (answer.question.risk_answer or '').strip().lower()
        answer_value = (answer.answer_value or '').strip().lower()

        if risk_answer and answer_value == risk_answer:
            score += 1

    if score <= 2:
        result_level = 'low'
    elif score <= 7:
        result_level = 'medium'
    else:
        result_level = 'high'

    return score, result_level


def calculate_early_dev_result(session):
    """
    Упрощённая логика:
    просто помечаем как done.
    Позже можно сделать более сложный скоринг.
    """
    score = 0
    result_level = 'done'
    return score, result_level


def calculate_session_result(session):
    template_type = session.template.template_type

    if template_type == 'mchat':
        return calculate_mchat_result(session)
    elif template_type == 'early_dev':
        return calculate_early_dev_result(session)

    return 0, 'unknown'