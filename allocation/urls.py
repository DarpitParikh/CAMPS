from django.urls import path
from .auth_views import login_view, logout_view, force_password_change
from .views import (
    dashboard, student_list, student_profile, add_student, delete_student,
    student_marks_download_csv, student_marks_download_pdf,
    bulk_delete_students, bulk_promote_students, download_selected_students,
    mark_attendance,
    marks_entry,
    manual_attendance_sheet_preview,
    allocate, preview, download_pdf, download_seating_excel, manage_roles, manage_subjects, upload_students, manage_enrollments,
    assign_subjects, upload_marksheet, public_result, public_result_pdf,
    edit_subject, delete_subject, attendance_report, attendance_summary_download, seating_home,
    download_student_upload_sample, download_marks_upload_sample,
    download_elective_upload_sample, download_seating_pdf_sample, sample_files,
    download_attendance_upload_sample,
    manage_notices, public_notices,
    webpush_public_key, webpush_subscribe, webpush_unsubscribe, service_worker
)

urlpatterns = [
    # Authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('force-password-change/', force_password_change, name='force_password_change'),
    
    # Public Home (Login)
    path('', login_view, name='public_home'),

    # Dashboard
    path('dashboard/', dashboard, name='dashboard'),
    
    # Student Management
    path('students/', student_list, name='student_list'),
    path('student/<int:student_id>/', student_profile, name='student_profile'),
    path('student/<int:student_id>/marks/csv/', student_marks_download_csv, name='student_marks_download_csv'),
    path('student/<int:student_id>/marks/pdf/', student_marks_download_pdf, name='student_marks_download_pdf'),
    path('student/<int:student_id>/delete/', delete_student, name='delete_student'),
    path('students/bulk-delete/', bulk_delete_students, name='bulk_delete_students'),
    path('students/bulk-promote/', bulk_promote_students, name='bulk_promote_students'),
    path('students/download-selected/', download_selected_students, name='download_selected_students'),
    path('students/add/', add_student, name='add_student'),
    
    # Attendance
    path('attendance/', mark_attendance, name='mark_attendance'),
    path('marks-entry/', marks_entry, name='marks_entry'),
    path('attendance/manual-sheet-preview/', manual_attendance_sheet_preview, name='manual_attendance_sheet_preview'),
    
    # Marks entry removed
    
    # CE Seating routes
    path('seating/allocate/', allocate, name='allocate'),
    path('seating/preview/', preview, name='preview'),
    path('seating/download-pdf/', download_pdf, name='download_pdf'),
    path('seating/download-excel/', download_seating_excel, name='download_seating_excel'),
    
    path('attendance-report/', attendance_report, name='attendance_report'),
    path('attendance-summary-download/', attendance_summary_download, name='attendance_summary_download'),

    # Admin helper
    path('faculty/manage/', manage_roles, name='manage_roles'),
    path('assign-subjects/', assign_subjects, name='assign_subjects'),
    path('notices/manage/', manage_notices, name='manage_notices'),

    # Subjects & Uploads
    path('subjects/', manage_subjects, name='manage_subjects'),
    path('subjects/<int:subject_id>/edit/', edit_subject, name='edit_subject'),
    path('subjects/<int:subject_id>/delete/', delete_subject, name='delete_subject'),
    path('students/upload/', upload_students, name='upload_students'),
    path('results/upload/', upload_marksheet, name='upload_marksheet'),
    path('enrollments/', manage_enrollments, name='manage_enrollments'),
    path('samples/students/', download_student_upload_sample, name='download_student_upload_sample'),
    path('samples/attendance-students/', download_attendance_upload_sample, name='download_attendance_upload_sample'),
    path('samples/marks/', download_marks_upload_sample, name='download_marks_upload_sample'),
    path('samples/electives/', download_elective_upload_sample, name='download_elective_upload_sample'),
    path('samples/seating-pdf/', download_seating_pdf_sample, name='download_seating_pdf_sample'),
    path('samples/', sample_files, name='sample_files'),

    # Public Results
    path('results/', public_result, name='public_result'),
    path('results/pdf/', public_result_pdf, name='public_result_pdf'),
    path('announcements/', public_notices, name='public_notices'),
    path('notifications/config/', webpush_public_key, name='webpush_public_key'),
    path('notifications/subscribe/', webpush_subscribe, name='webpush_subscribe'),
    path('notifications/unsubscribe/', webpush_unsubscribe, name='webpush_unsubscribe'),
    path('sw.js', service_worker, name='service_worker'),
]
