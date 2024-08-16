from rest_framework.permissions import BasePermission

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Doctors').exists()

class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Patients').exists()


class IsPatientAndDoctorInSameDepartment(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.groups.filter(name='Patients').exists():
            return obj.patient == user and obj.patient.department == user.department
        if user.groups.filter(name='Doctors').exists():
            return obj.patient.department == user.department
        return False


class IsRelevantDoctor(BasePermission):
    def has_object_permission(self, request, view, obj):
       
        if request.user == obj:
            return True
        if request.user.groups.filter(name='Doctor').exists() and request.user.department == obj.department:
            return True
        return False

class IsDoctorsInDepartment(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.groups.filter(name='Doctors').exists():
            return obj.department == user.department
        return False

class IsOwnProfile(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj