from django.urls import path
from .views import (
    ActivityCategoryListView,
    ActivityListView,
    ActivityDetailView,
    ActivityCompleteView,
    ChildActivityHistoryView,
)

urlpatterns = [
    path('categories/', ActivityCategoryListView.as_view(), name='activity-categories'),
    path('', ActivityListView.as_view(), name='activity-list'),
    path('<int:activity_id>/', ActivityDetailView.as_view(), name='activity-detail'),
    path('<int:activity_id>/complete/', ActivityCompleteView.as_view(), name='activity-complete'),
    path('children/<int:child_id>/history/', ChildActivityHistoryView.as_view(), name='child-activity-history'),
]