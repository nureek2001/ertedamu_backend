from django.db import transaction
from rest_framework import serializers

from families.models import Child, FamilyMembership
from families.serializers import ChildSerializer
from families.utils import calculate_age_months

from .models import (
    ScreeningTemplate,
    ScreeningQuestion,
    ScreeningSession,
    ScreeningAnswer,
)
from .utils import can_start_screening, calculate_session_result


class ScreeningQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreeningQuestion
        fields = [
            'id',
            'order',
            'text',
            'answer_type',
            'is_required',
        ]


class ScreeningTemplateSerializer(serializers.ModelSerializer):
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = ScreeningTemplate
        fields = [
            'id',
            'title',
            'code',
            'template_type',
            'description',
            'min_age_months',
            'max_age_months',
            'version',
            'is_active',
            'cooldown_days',
            'questions_count',
        ]

    def get_questions_count(self, obj):
        return obj.questions.count()


class ScreeningTemplateDetailSerializer(serializers.ModelSerializer):
    questions = ScreeningQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = ScreeningTemplate
        fields = [
            'id',
            'title',
            'code',
            'template_type',
            'description',
            'min_age_months',
            'max_age_months',
            'version',
            'is_active',
            'cooldown_days',
            'questions',
        ]


class ScreeningAnswerSerializer(serializers.ModelSerializer):
    question = ScreeningQuestionSerializer(read_only=True)
    question_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ScreeningAnswer
        fields = [
            'id',
            'question',
            'question_id',
            'answer_value',
        ]
        read_only_fields = ['id']

    def validate_question_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Некорректный question_id.")
        return value


class ScreeningSessionSerializer(serializers.ModelSerializer):
    child = ChildSerializer(read_only=True)
    template = ScreeningTemplateSerializer(read_only=True)
    answers = ScreeningAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = ScreeningSession
        fields = [
            'id',
            'child',
            'template',
            'status',
            'result_level',
            'score',
            'target_age_months',
            'started_at',
            'completed_at',
            'notes',
            'answers',
        ]


class ScreeningSessionCreateSerializer(serializers.Serializer):
    child_id = serializers.IntegerField()
    template_code = serializers.CharField()
    target_age_months = serializers.IntegerField(required=False)

    def validate_child_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Некорректный child_id.")
        return value

    def validate_template_code(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        request = self.context['request']
        child_id = attrs['child_id']
        template_code = attrs['template_code']

        child = Child.objects.filter(pk=child_id).select_related('family').first()
        if not child:
            raise serializers.ValidationError({"child_id": "Ребёнок не найден."})

        membership = FamilyMembership.objects.filter(
            user=request.user,
            family=child.family
        ).first()
        if not membership or not membership.can_view_screenings:
            raise serializers.ValidationError({"detail": "Нет доступа к скринингам этого ребёнка."})

        template = ScreeningTemplate.objects.filter(code=template_code, is_active=True).first()
        if not template:
            raise serializers.ValidationError({"template_code": "Шаблон скрининга не найден."})

        allowed, reason = can_start_screening(child, template)
        if not allowed:
            raise serializers.ValidationError({"detail": reason})

        attrs['child'] = child
        attrs['template'] = template
        return attrs

    def create(self, validated_data):
        child = validated_data['child']
        template = validated_data['template']

        target_age_months = validated_data.get('target_age_months')
        if target_age_months is None:
            target_age_months = calculate_age_months(child.birth_date)

        session = ScreeningSession.objects.create(
            child=child,
            template=template,
            target_age_months=target_age_months,
        )
        return session


class ScreeningAnswerBulkUpsertSerializer(serializers.Serializer):
    answers = serializers.ListField(child=serializers.DictField(), allow_empty=False)

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("Список ответов пуст.")
        return value

    @transaction.atomic
    def save_answers(self, session):
        template_question_ids = set(
            session.template.questions.values_list('id', flat=True)
        )

        saved_answers = []

        for item in self.validated_data['answers']:
            question_id = item.get('question_id')
            answer_value = item.get('answer_value')

            if not question_id:
                raise serializers.ValidationError({"question_id": "question_id обязателен."})

            if question_id not in template_question_ids:
                raise serializers.ValidationError(
                    {"question_id": f"Вопрос {question_id} не принадлежит шаблону {session.template.code}."}
                )

            if answer_value in [None, '']:
                raise serializers.ValidationError(
                    {"answer_value": f"Ответ для вопроса {question_id} не может быть пустым."}
                )

            question = ScreeningQuestion.objects.get(pk=question_id)

            answer, _ = ScreeningAnswer.objects.update_or_create(
                session=session,
                question=question,
                defaults={'answer_value': str(answer_value).strip().lower()}
            )
            saved_answers.append(answer)

        return saved_answers


class ScreeningSubmitSerializer(serializers.Serializer):
    confirm = serializers.BooleanField(default=True)

    def finalize(self, session):
        if session.status == 'completed':
            raise serializers.ValidationError("Сессия уже завершена.")

        required_questions_count = session.template.questions.filter(is_required=True).count()
        current_answers_count = session.answers.count()

        if current_answers_count < required_questions_count:
            raise serializers.ValidationError(
                f"Не все обязательные вопросы заполнены. "
                f"Ожидается {required_questions_count}, получено {current_answers_count}."
            )

        score, result_level = calculate_session_result(session)
        session.complete(score=score, result_level=result_level)
        return session


class ScreeningAvailabilitySerializer(serializers.Serializer):
    template = ScreeningTemplateSerializer()
    available = serializers.BooleanField()
    reason = serializers.CharField(allow_null=True)