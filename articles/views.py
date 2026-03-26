from rest_framework import generics, permissions

from families.models import Child, FamilyMembership
from .models import Article
from .serializers import ArticleSerializer
from families.utils import calculate_age_months

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

class ArticleListAPIView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Article.objects.filter(is_active=True)

        category = self.request.query_params.get("category")
        search = self.request.query_params.get("search")
        child_id = self.request.query_params.get("child_id")

        if category and category != "all":
            queryset = queryset.filter(category=category)

        if search:
            queryset = queryset.filter(title__icontains=search)

        if child_id:
            child, membership = get_child_for_user(self.request.user, child_id)
            if not child:
                return Response({"detail": "Ребёнок не найден или нет доступа."}, status=status.HTTP_404_NOT_FOUND)

            age_months = calculate_age_months(child.birth_date)
            queryset = queryset.filter(
                min_months__lte=age_months,
                max_months__gte=age_months,
            )

        return queryset


class ArticleDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Article.objects.filter(is_active=True)