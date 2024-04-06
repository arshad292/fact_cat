from django.db import models

# Create your models here.

class CatFact(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)