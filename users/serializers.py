from rest_framework import serializers
from .models import Department

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

from django.contrib.auth import get_user_model

class CustomUserSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    group = serializers.StringRelatedField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'department', 'group']

from .models import PatientRecord

class PatientRecordSerializer(serializers.ModelSerializer):
    patient = serializers.StringRelatedField()
    department = serializers.StringRelatedField()

    class Meta:
        model = PatientRecord
        fields = '__all__'
