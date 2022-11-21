from django.db import models

# Create your models here.

class User(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=99999, default="not found")
    Name = models.CharField(max_length=100, default="not found")
    rating = models.CharField(max_length=10, default="not found")