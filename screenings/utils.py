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


MCHAT_INTERPRETATIONS = {
    "low": {
        "summary": "Низкий риск. По результатам скрининга выраженных признаков не выявлено.",
        "recommendations": [
            "Продолжайте наблюдать за развитием ребёнка.",
            "Повторите скрининг в плановые сроки, если это рекомендовано по возрасту.",
        ],
    },
    "medium": {
        "summary": "Средний риск. Есть ответы, требующие дополнительного внимания.",
        "recommendations": [
            "Рекомендуется обсудить результаты с педиатром.",
            "При необходимости пройти дополнительную оценку развития.",
        ],
    },
    "high": {
        "summary": "Высокий риск. Рекомендуется обратиться к специалисту для более подробной оценки.",
        "recommendations": [
            "Обратитесь к педиатру или детскому неврологу.",
            "Не откладывайте дополнительную диагностику и наблюдение.",
        ],
    },
}


EARLY_DEV_RECOMMENDATIONS = {
    1: "Чаще устанавливайте зрительный контакт и используйте яркие игрушки для привлечения внимания.",
    2: "Стимулируйте слух: разговаривайте с ребёнком, используйте погремушки, музыкальные игрушки.",
    3: "Больше улыбайтесь ребёнку, играйте лицом к лицу, поощряйте эмоциональный контакт.",
    4: "Полезно чаще выкладывать ребёнка на животик и постепенно укреплять мышцы шеи и спины.",
    5: "Стимулируйте движение игрушками и создавайте безопасное пространство для активности.",
    6: "Предлагайте удобные для захвата игрушки и поощряйте тянуться к ним.",
    7: "Развивайте координацию обеих рук с помощью безопасных небольших предметов.",
    8: "Чаще разговаривайте с ребёнком, повторяйте его звуки, пойте песенки.",
    9: "Чаще зовите ребёнка по имени и поощряйте отклик.",
    10: "Используйте простые короткие фразы и повторяйте их в повседневных ситуациях.",
    11: "Увеличьте количество совместных игр и эмоционального общения.",
    12: "Показывайте, как играть с игрушками, исследуйте предметы вместе.",
    13: "Создайте безопасные условия для вставания, ходьбы вдоль опоры и первых шагов.",
    14: "Стимулируйте жесты в игре: машите рукой, показывайте на предметы, просите показать.",
    15: "Называйте предметы и действия, читайте книги с картинками, поощряйте речь.",
}


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


def get_mchat_analysis(session):
    answers = session.answers.select_related('question').all()
    detailed_analysis = []

    for answer in answers:
        question = answer.question
        answer_value = (answer.answer_value or '').strip().lower()
        risk_answer = (question.risk_answer or '').strip().lower()

        is_risk = bool(risk_answer and answer_value == risk_answer)

        detailed_analysis.append({
            "question_id": question.id,
            "order": question.order,
            "question_text": question.text,
            "answer_value": answer_value,
            "status": "risk" if is_risk else "ok",
            "is_risk": is_risk,
        })

    score = session.score
    result_level = session.result_level
    meta = MCHAT_INTERPRETATIONS.get(result_level, {
        "summary": "Результат скрининга получен.",
        "recommendations": [],
    })

    return {
        "score": score,
        "result_level": result_level,
        "summary": meta["summary"],
        "detailed_analysis": detailed_analysis,
        "general_recommendations": meta["recommendations"],
    }


def calculate_early_dev_result(session):
    """
    Для early_dev:
    risk = количество ответов, совпавших с risk_answer.
    Обычно risk_answer='no', то есть отсутствие навыка = зона внимания.
    """
    score = 0
    answers = session.answers.select_related('question').all()

    for answer in answers:
        risk_answer = (answer.question.risk_answer or '').strip().lower()
        answer_value = (answer.answer_value or '').strip().lower()

        if risk_answer and answer_value == risk_answer:
            score += 1

    if score == 0:
        result_level = 'low'
    elif score <= 3:
        result_level = 'medium'
    else:
        result_level = 'high'

    return score, result_level


def get_early_dev_analysis(session):
    answers = session.answers.select_related('question').all()
    detailed_analysis = []
    risk_count = 0

    for answer in answers:
        question = answer.question
        answer_value = (answer.answer_value or '').strip().lower()
        risk_answer = (question.risk_answer or '').strip().lower()

        is_risk = bool(risk_answer and answer_value == risk_answer)
        if is_risk:
            risk_count += 1

        detailed_analysis.append({
            "question_id": question.id,
            "order": question.order,
            "question_text": question.text,
            "answer_value": answer_value,
            "status": "attention" if is_risk else "ok",
            "recommendation": EARLY_DEV_RECOMMENDATIONS.get(question.order) if is_risk else None,
        })

    if risk_count == 0:
        summary = "Развитие ребёнка по отмеченным навыкам соответствует ожидаемому уровню."
        general_recommendations = [
            "Продолжайте поддерживать развитие ребёнка через общение, игру и ежедневную активность."
        ]
        result_level = "low"
    elif risk_count <= 3:
        summary = "Есть отдельные навыки, которым стоит уделить дополнительное внимание."
        general_recommendations = [
            "Наблюдайте за развитием ребёнка в динамике.",
            "Повторите скрининг позже.",
            "Регулярно выполняйте простые развивающие упражнения."
        ]
        result_level = "medium"
    else:
        summary = "Выявлено несколько зон внимания в развитии ребёнка."
        general_recommendations = [
            "Рекомендуется консультация педиатра или профильного специалиста.",
            "Повторите оценку развития после наблюдения и развивающих занятий.",
            "Уделите особое внимание навыкам, отмеченным ниже."
        ]
        result_level = "high"

    return {
        "score": risk_count,
        "result_level": result_level,
        "summary": summary,
        "target_age_months": session.target_age_months,
        "detailed_analysis": detailed_analysis,
        "general_recommendations": general_recommendations,
    }


def build_session_result_payload(session):
    payload = {
        "session_id": session.id,
        "template_code": session.template.code,
        "template_type": session.template.template_type,
        "status": session.status,
        "score": session.score,
        "result_level": session.result_level,
        "target_age_months": session.target_age_months,
        "started_at": session.started_at,
        "completed_at": session.completed_at,
    }

    if session.template.template_type == 'mchat':
        payload.update(get_mchat_analysis(session))
    elif session.template.template_type == 'early_dev':
        payload.update(get_early_dev_analysis(session))

    return payload


def calculate_session_result(session):
    template_type = session.template.template_type

    if template_type == 'mchat':
        return calculate_mchat_result(session)
    elif template_type == 'early_dev':
        return calculate_early_dev_result(session)

    return 0, 'unknown'