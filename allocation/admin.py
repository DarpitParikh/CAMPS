from django.contrib import admin
from .models import (
    Branch, Semester, Subject, Faculty, Student, StudentSubject,
    Attendance, Marks, CESeating
)

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['number']
    ordering = ['number']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'branch', 'semester', 'max_marks']
    list_filter = ['branch', 'semester']
    search_fields = ['code', 'name']

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'employee_id', 'get_subjects_count', 'last_subject']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name']
    filter_horizontal = ['subjects']
    
    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Name'
    
    def get_subjects_count(self, obj):
        return obj.subjects.count()
    get_subjects_count.short_description = 'Subjects Count'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['enrollment_no', 'name', 'branch', 'semester', 'division', 'mentor_name']
    list_filter = ['branch', 'semester', 'division']
    search_fields = ['enrollment_no', 'name', 'mentor_name']
    readonly_fields = ['exam_no', 'room_no', 'seat_no']

@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject']
    list_filter = ['subject__semester']
    search_fields = ['student__enrollment_no', 'subject__code']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'status', 'marked_by']
    list_filter = ['status', 'date', 'subject']
    search_fields = ['student__enrollment_no']
    date_hierarchy = 'date'
    readonly_fields = ['marked_by']

@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'internal', 'external', 'get_total', 'get_grade', 'is_pass', 'submitted']
    list_filter = ['subject', 'submitted', 'subject__semester']
    search_fields = ['student__enrollment_no', 'subject__code']
    readonly_fields = ['submitted_date']
    
    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Total'
    
    def get_grade(self, obj):
        return obj.get_grade()
    get_grade.short_description = 'Grade'

@admin.register(CESeating)
class CESeatingAdmin(admin.ModelAdmin):
    list_display = ['room_no', 'seat_from', 'seat_to', 'count']
    list_filter = ['room_no']
    ordering = ['room_no']
