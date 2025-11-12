from django.db import models
from django.conf import settings

class Item(models.Model):
    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='items'
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items'
    )
    item_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=100, blank=True)
    unique_marks = models.CharField(max_length=255, blank=True)
    main_photo_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    initial_found_time = models.DateTimeField(null=True, blank=True)
    final_found_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.item_name} ({self.owner_user})"
