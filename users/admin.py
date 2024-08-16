from django.contrib import admin
from .models import CustomUser,Department,PatientRecord
# Register your models here.
#admin.site.register(CustomUser)
admin.site.register(Department)
admin.site.register(PatientRecord)