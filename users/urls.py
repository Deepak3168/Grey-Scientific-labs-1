from django.urls import path
from .views import login,logout,register,doctor_detail,patient_detail,patient_record_detail
from .views import PatientRecordListCreateView,DoctorsListCreateView,PatientListCreateView,patient_detail,DepartmentListCreateView



urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('api/register/', register, name='register'),
     path('patient_records/', PatientRecordListCreateView.as_view(), name='patient_records_list_create'),
    path('patient_records/<int:pk>/', patient_record_detail, name='patient_record_detail'),
    path('doctors/',DoctorsListCreateView.as_view(),name='doctors'),
    path('doctors/<int:pk>/',doctor_detail,name='doctor'),
    path('patients/',PatientListCreateView.as_view(),name='patients'),
    path('patients/<int:pk>',patient_detail,name='patient'),
    path('departments/',DepartmentListCreateView.as_view(),name='departments'),
]

