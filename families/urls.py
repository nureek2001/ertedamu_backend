from django.urls import path
from .views import (
    CreateMyFamilyView,
    MyFamilyView,
    FamilyMembersView,
    FamilyMemberDetailView,
    ChildListCreateView,
    ChildDetailView,
    ChildMeasurementListCreateView,
    SetActiveChildView,
    MyActiveChildView,
    DashboardView,
)

urlpatterns = [
    path('my/create/', CreateMyFamilyView.as_view(), name='create-my-family'),
    path('my/', MyFamilyView.as_view(), name='my-family'),

    path('my/members/', FamilyMembersView.as_view(), name='family-members'),
    path('my/members/<int:pk>/', FamilyMemberDetailView.as_view(), name='family-member-detail'),

    path('children/', ChildListCreateView.as_view(), name='children-list-create'),
    path('children/<int:pk>/', ChildDetailView.as_view(), name='child-detail'),
    path('children/<int:child_id>/measurements/', ChildMeasurementListCreateView.as_view(), name='child-measurements'),

    path('active-child/', MyActiveChildView.as_view(), name='my-active-child'),
    path('active-child/set/', SetActiveChildView.as_view(), name='set-active-child'),

    path('dashboard/', DashboardView.as_view(), name='family-dashboard'),
]