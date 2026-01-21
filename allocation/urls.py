from django.urls import path
from .auth_views import login_view, logout_view
from .views import (
    dashboard, student_list, student_profile, add_student, delete_student,
    mark_attendance,
    allocate, preview, download_pdf, manage_roles, manage_subjects, upload_students, manage_enrollments,
    assign_subjects
)

urlpatterns = [
    # Authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Dashboard
    path('', dashboard, name='dashboard'),
    
    # Student Management
    path('students/', student_list, name='student_list'),
    path('student/<int:student_id>/', student_profile, name='student_profile'),
    path('student/<int:student_id>/delete/', delete_student, name='delete_student'),
    path('students/add/', add_student, name='add_student'),
    
    # Attendance
    path('attendance/', mark_attendance, name='mark_attendance'),
    
    # Marks entry removed
    
    # Exam Seating (Existing)
    path('allocate/', allocate, name='allocate'),
    path('preview/', preview, name='preview'),
    path('download/', download_pdf, name='download'),

    # Admin helper
    path('admin/roles/', manage_roles, name='manage_roles'),
    path('assign-subjects/', assign_subjects, name='assign_subjects'),

    # Subjects & Uploads
    path('subjects/', manage_subjects, name='manage_subjects'),
    path('students/upload/', upload_students, name='upload_students'),
    path('enrollments/', manage_enrollments, name='manage_enrollments'),
]
