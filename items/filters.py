import django_filters
from .models import Item

class ItemFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category__id')
    color = django_filters.CharFilter(field_name='color', lookup_expr='icontains')
    unique_marks = django_filters.CharFilter(field_name='color', lookup_expr='icontains')
    description = django_filters.CharFilter(field_name='color', lookup_expr='icontains')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    initial_found_after = django_filters.DateTimeFilter(field_name='initial_found_time', lookup_expr='gte')
    final_found_before = django_filters.DateTimeFilter(field_name='final_found_time', lookup_expr='lte')

    class Meta:
        model = Item
        fields = ['category', 'unique_marks','description','color', 'created_after', 'created_before', 'initial_found_after', 'final_found_before']
