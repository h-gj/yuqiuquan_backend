from django.db import models

# Create your models here.


class ChangeDiSub(models.Model):
    sub_date = models.DateField()
    sub_start_time = models.DateTimeField(max_length=6)
    sub_end_time = models.DateTimeField(max_length=6)
    sub_email = models.CharField(max_length=50)
    create_time = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)
