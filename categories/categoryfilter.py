import django_filters
from .models import Category

class CategoryFilter(django_filters.FilterSet):
    category_name = django_filters.CharFilter(field_name='category_name', lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['parent_category', 'category_name']
