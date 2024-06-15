from django.db import models
from django.utils import timezone
# Create your models here.
class UserId(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=255)
    expiry_date = models.DateTimeField(timezone.now)
    id = models.CharField(max_length=255,unique=True,primary_key=True)

    def __str__(self) -> str:
        return self.id