from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import PatientRecord, Department
from .serializers import PatientRecordSerializer, DepartmentSerializer,CustomUserSerializer
from .permissions import IsDoctor, IsPatient,IsDoctorsInDepartment,IsPatientAndDoctorInSameDepartment,IsRelevantDoctor,IsOwnProfile
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from .models import CustomUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from rest_framework import status
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    group_name = request.data.get('group')

    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return Response({'error': 'Invalid group name'}, status=400)

   
    user = CustomUser.objects.create(
        username=username,
        password=make_password(password),
        group=group
    )

    return Response({'message': 'User registered successfully'})


User = get_user_model()
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    
    user = User.objects.filter(email=email).first()
    
    if user:
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({'access_token': str(refresh.access_token)})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        response = requests.post(f"{settings.APP2_AUTH_URL}/login", data={
            'email': email,
            'password': password
        })

        if response.status_code == 200:
            user_data = response.json()
            user = User.objects.create(
                email=email,
                username=user_data['username'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                group_name = user_data.get('group',''),
                department_name = user_data.get('department',''),
            )
            user.set_password(password) 
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response({'access_token': str(refresh.access_token)})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def logout(request):
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PatientRecordListCreateView(generics.ListCreateAPIView):
    queryset = PatientRecord.objects.all()
    serializer_class = PatientRecordSerializer
    permission_classes = [IsAuthenticated,IsDoctorsInDepartment]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Doctors').exists():
            return self.queryset.filter(department__in=user.doctor.departments.all())
        return self.queryset.none()

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsRelevantDoctor])
def patient_record_detail(request, pk):
    try:
        record = PatientRecord.objects.get(pk=pk)
    except PatientRecord.DoesNotExist:
        return Response({'error': 'Patient record not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user != record.patient and not (request.user.groups.filter(name='Doctor').exists() and request.user.department == record.department):
        return Response({'error': 'You do not have permission to access this record'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = PatientRecordSerializer(record)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PatientRecordSerializer(record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        record.delete()
        return Response({'message': 'Patient record deleted'}, status=status.HTTP_204_NO_CONTENT)



class DoctorsListCreateView(generics.ListCreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        doctor_group = Group.objects.get(name='Doctors')
        return CustomUser.objects.filter(groups=doctor_group)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsOwnProfile])
def doctor_detail(request, pk):
    try:
        doctor = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user != doctor:
        return Response({'error': 'You do not have permission to access this profile'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = CustomUserSerializer(doctor)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CustomUserSerializer(doctor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        doctor.delete()
        return Response({'message': 'Doctor profile deleted'}, status=status.HTTP_204_NO_CONTENT)


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        return CustomUser.objects.filter(groups__name='Patients')

    def perform_create(self, serializer):
        if not self.request.user.groups.filter(name='Doctors').exists():
            raise PermissionDenied('Only doctors can create new patients.')
        serializer.save()


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def patient_detail(request, pk):
    try:
        patient = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user != patient and not request.user.groups.filter(name='Doctor').exists():
        if not request.user.groups.filter(name='Doctor').exists() or request.user.department != patient.department:
            return Response({'error': 'You do not have permission to access this patient\'s record'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = CustomUserSerializer(patient)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CustomUserSerializer(patient, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        patient.delete()
        return Response({'message': 'Patient record deleted'}, status=status.HTTP_204_NO_CONTENT)

class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

@api_view(['POST'])
def create_or_update_user_from_app2(request):
    email = request.data.get('email')
    username = request.data.get('username')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    group_name = request.data.get('group')
    department_name = request.data.get('department')

    if not email or not username:
        return Response({'error': 'Email and username are required.'}, status=status.HTTP_400_BAD_REQUEST)
    group, _ = Group.objects.get_or_create(name=group_name)
    department, _ = Department.objects.get_or_create(name=department_name)
    
    user, created = User.objects.update_or_create(
        email=email,
        defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'group': group,
            'department': department
        }
    )
    
    return Response({'status': 'User created or updated', 'created': created}, status=status.HTTP_200_OK)
