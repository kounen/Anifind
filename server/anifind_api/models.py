from django.db import models 


# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=99999, default="", primary_key=True)
    password = models.CharField(max_length=99999, default="none")
    ratings = models.JSONField(default="")
    # user_id = models.CharField(max_length=99999, default="")
    # Name = models.CharField(max_length=100, default="")
    # rating = models.CharField(max_length=10, default="")