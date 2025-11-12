from rest_framework import serializers
from .models import Item
from categories.models import Category
from categories.serializers import CategorySerializer

class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Item
        fields = [
            'id',
            'owner_user',
            'item_name',
            'description',
            'category',
            'category_id',
            'color',
            'unique_marks',
            'main_photo_url',
            'created_at',
            'initial_found_time',
            'final_found_time'
        ]
        read_only_fields = ['id', 'created_at']
