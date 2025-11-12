from rest_framework import viewsets, permissions
from .models import Item
from .serializers import ItemSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ItemFilter

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all().order_by('-created_at')
    serializer_class = ItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemFilter
    ordering_fields = ['created_at', 'initial_found_time', 'final_found_time', 'item_name']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
