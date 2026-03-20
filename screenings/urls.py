from django.urls import path
from .views import (
    ScreeningTemplateListView,
    ScreeningTemplateDetailView,
    ScreeningAvailabilityView,
    ScreeningSessionCreateView,
    ScreeningSessionDetailView,
    ScreeningSessionAnswersUpsertView,
    ScreeningSessionSubmitView,
    ChildScreeningHistoryView,
    ChildLatestScreeningView,
)

urlpatterns = [
    path('templates/', ScreeningTemplateListView.as_view(), name='screening-templates'),
    path('templates/<str:code>/', ScreeningTemplateDetailView.as_view(), name='screening-template-detail'),

    path('children/<int:child_id>/availability/', ScreeningAvailabilityView.as_view(), name='screening-availability'),
    path('children/<int:child_id>/history/', ChildScreeningHistoryView.as_view(), name='child-screening-history'),
    path('children/<int:child_id>/latest/', ChildLatestScreeningView.as_view(), name='child-latest-screening'),

    path('sessions/', ScreeningSessionCreateView.as_view(), name='screening-session-create'),
    path('sessions/<int:session_id>/', ScreeningSessionDetailView.as_view(), name='screening-session-detail'),
    path('sessions/<int:session_id>/answers/', ScreeningSessionAnswersUpsertView.as_view(), name='screening-session-answers'),
    path('sessions/<int:session_id>/submit/', ScreeningSessionSubmitView.as_view(), name='screening-session-submit'),
]