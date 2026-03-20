from django.urls import path
from .views import (
    MilestoneCategoryListView,
    MilestoneListView,
    MilestoneDetailView,
    MilestoneToggleView,
    ChildMilestoneProgressView,
)

urlpatterns = [
    path('categories/', MilestoneCategoryListView.as_view(), name='milestone-categories'),
    path('', MilestoneListView.as_view(), name='milestone-list'),
    path('<int:milestone_id>/', MilestoneDetailView.as_view(), name='milestone-detail'),
    path('<int:milestone_id>/toggle/', MilestoneToggleView.as_view(), name='milestone-toggle'),
    path('children/<int:child_id>/progress/', ChildMilestoneProgressView.as_view(), name='child-milestone-progress'),
]