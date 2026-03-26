from django.urls import path
from .views import (
    ActivityCategoryListAPIView,
    ActivityListAPIView,
    ActivityDetailAPIView,
    ActivityCompletionCreateAPIView,
    ChildActivityHistoryAPIView,
)

urlpatterns = [
    path("categories/", ActivityCategoryListAPIView.as_view(), name="activity-categories"),
    path("", ActivityListAPIView.as_view(), name="activity-list"),
    path("<int:pk>/", ActivityDetailAPIView.as_view(), name="activity-detail"),
    path("<slug:activity_slug>/complete/", ActivityCompletionCreateAPIView.as_view(), name="activity-complete"),
    path("children/<int:child_id>/history/", ChildActivityHistoryAPIView.as_view(), name="activity-history"),
]