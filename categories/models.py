from django.db import models

class Category(models.Model):
    category_name = models.CharField(max_length=255 , unique=True)
    parent_category = models.ForeignKey(
        'self',
        on_delete= models.SET_NULL,
        null= True ,
        blank= True ,
        related_name= 'subcategories'
    )
    def __str__(self):
        return self.category_name