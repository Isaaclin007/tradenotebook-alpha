from django.db import models

# Create your models here.

class Result(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    model_input = models.CharField(max_length = 100)
    delivered = models.BooleanField(default=False)
    ip_address = models.CharField(max_length = 15)
    class Meta:
        ordering = ['created']