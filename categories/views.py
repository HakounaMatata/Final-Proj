from rest_framework import viewsets, permissions
from .models import Category
from .serializers import CategorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from .categoryfilter import CategoryFilter

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('category_name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter