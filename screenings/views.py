from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from families.models import Child, FamilyMembership

from .models import ScreeningTemplate, ScreeningSession
from .serializers import (
    ScreeningTemplateSerializer,
    ScreeningTemplateDetailSerializer,
    ScreeningSessionSerializer,
    ScreeningSessionCreateSerializer,
    ScreeningAnswerBulkUpsertSerializer,
    ScreeningSubmitSerializer,
)
from .utils import can_start_screening


def get_child_for_user(user, child_id):
    child = Child.objects.filter(pk=child_id).select_related('family').first()
    if not child:
        return None, None

    membership = FamilyMembership.objects.filter(
        user=user,
        family=child.family
    ).first()

    if not membership:
        return None, None

    return child, membership


def get_session_for_user(user, session_id):
    session = (
        ScreeningSession.objects.select_related(
            'child',
            'child__family',
            'template',
        ).prefetch_related(
            'answers__question',
            'template__questions',
        ).filter(pk=session_id).first()
    )

    if not session:
        return None, None

    membership = FamilyMembership.objects.filter(
        user=user,
        family=session.child.family
    ).first()

    if not membership:
        return session, None

    return session, membership


class ScreeningTemplateListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        templates = ScreeningTemplate.objects.filter(is_active=True).prefetch_related('questions')
        return Response(ScreeningTemplateSerializer(templates, many=True).data)


class ScreeningTemplateDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, code):
        template = get_object_or_404(
            ScreeningTemplate.objects.prefetch_related('questions'),
            code=code,
            is_active=True
        )
        return Response(ScreeningTemplateDetailSerializer(template).data)


class ScreeningAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, child_id):
        child, membership = get_child_for_user(request.user, child_id)
        if not child:
            return Response(
                {"detail": "Ребёнок не найден или нет доступа."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not membership.can_view_screenings:
            return Response(
                {"detail": "Нет прав на просмотр скринингов."},
                status=status.HTTP_403_FORBIDDEN
            )

        templates = ScreeningTemplate.objects.filter(is_active=True)
        data = []

        for template in templates:
            available, reason = can_start_screening(child, template)
            data.append({
                "template": ScreeningTemplateSerializer(template).data,
                "available": available,
                "reason": reason,
            })

        return Response(data)


class ScreeningSessionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ScreeningSessionCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        session = serializer.save()

        session = (
            ScreeningSession.objects.select_related(
                'child',
                'child__family',
                'template'
            ).prefetch_related(
                'answers__question',
                'template__questions'
            ).get(pk=session.pk)
        )

        return Response(ScreeningSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class ScreeningSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session, membership = get_session_for_user(request.user, session_id)

        if not session:
            return Response({"detail": "Сессия не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not membership or not membership.can_view_screenings:
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        return Response(ScreeningSessionSerializer(session).data)


class ScreeningSessionAnswersUpsertView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session, membership = get_session_for_user(request.user, session_id)

        if not session:
            return Response({"detail": "Сессия не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not membership or not membership.can_view_screenings:
            return Response({"detail": "Нет доступа к скринингам."}, status=status.HTTP_403_FORBIDDEN)

        if session.status == 'completed':
            return Response(
                {"detail": "Нельзя изменять завершённую сессию."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ScreeningAnswerBulkUpsertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save_answers(session)

        session = (
            ScreeningSession.objects.select_related(
                'child',
                'child__family',
                'template'
            ).prefetch_related(
                'answers__question',
                'template__questions'
            ).get(pk=session.pk)
        )

        return Response(ScreeningSessionSerializer(session).data)


class ScreeningSessionSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session, membership = get_session_for_user(request.user, session_id)

        if not session:
            return Response({"detail": "Сессия не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not membership or not membership.can_view_screenings:
            return Response({"detail": "Нет доступа к скринингам."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ScreeningSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.finalize(session)

        session = (
            ScreeningSession.objects.select_related(
                'child',
                'child__family',
                'template'
            ).prefetch_related(
                'answers__question',
                'template__questions'
            ).get(pk=session.pk)
        )

        return Response(ScreeningSessionSerializer(session).data)


class ChildScreeningHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, child_id):
        child, membership = get_child_for_user(request.user, child_id)
        if not child:
            return Response(
                {"detail": "Ребёнок не найден или нет доступа."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not membership.can_view_screenings:
            return Response(
                {"detail": "Нет прав на просмотр скринингов."},
                status=status.HTTP_403_FORBIDDEN
            )

        sessions = ScreeningSession.objects.select_related(
            'template',
            'child'
        ).prefetch_related(
            'answers__question',
            'template__questions'
        ).filter(child=child).order_by('-completed_at', '-started_at')

        template_code = request.query_params.get('template')
        if template_code:
            sessions = sessions.filter(template__code=template_code)

        return Response(ScreeningSessionSerializer(sessions, many=True).data)


class ChildLatestScreeningView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, child_id):
        child, membership = get_child_for_user(request.user, child_id)
        if not child:
            return Response(
                {"detail": "Ребёнок не найден или нет доступа."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not membership.can_view_screenings:
            return Response(
                {"detail": "Нет прав на просмотр скринингов."},
                status=status.HTTP_403_FORBIDDEN
            )

        session = ScreeningSession.objects.select_related(
            'template',
            'child'
        ).prefetch_related(
            'answers__question',
            'template__questions'
        ).filter(
            child=child,
            status='completed'
        ).order_by('-completed_at', '-started_at').first()

        if not session:
            return Response(
                {"detail": "Завершённых скринингов пока нет."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(ScreeningSessionSerializer(session).data)