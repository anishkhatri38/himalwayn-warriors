from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import User

class FitnessPlan(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    premium = models.BooleanField(default=True)


