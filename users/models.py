from django.db import models
from django.contrib.auth.models import AbstractUser, Group

class Department(models.Model):
    name = models.CharField(max_length=100)
    diagnostics = models.TextField()
    location = models.CharField(max_length=245)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='users')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name='users')

    def __str__(self):
        return self.username


from django.conf import settings

class PatientRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='records')
    created_date = models.DateTimeField(auto_now_add=True)
    diagnostics = models.TextField()
    observations = models.TextField()
    treatments = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='records')
    misc = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Record {self.record_id} for {self.patient.username}'
