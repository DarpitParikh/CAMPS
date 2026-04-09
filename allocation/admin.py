from django.contrib import admin
from .models import (
    Branch, Semester, Subject, Faculty, Student, StudentSubject,
    Attendance, CESeating, Notice, PushSubscription, NoticeAttachment, StudentMark,
    MentorActionLog, MarksFreezeRule, MarksAuditTrail, MentorAssignment
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
    list_display = ['code', 'name', 'branch', 'semester', 'credit', 'is_elective', 'elective_group']
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
    list_display = ['enrollment_no', 'name', 'branch', 'semester', 'division', 'admission_year', 'mentor_name']
    list_filter = ['branch', 'semester', 'division', 'admission_year']
    search_fields = ['enrollment_no', 'name', 'mentor_name', 'admission_year']
    readonly_fields = ['exam_no', 'room_no']

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

@admin.register(CESeating)
class CESeatingAdmin(admin.ModelAdmin):
    list_display = ['room_no', 'seat_from', 'seat_to', 'count']
    list_filter = ['room_no']
    ordering = ['room_no']


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'notice_type', 'is_published', 'published_at', 'created_by', 'get_attachment_count', 'created_at']
    list_filter = ['notice_type', 'is_published']
    search_fields = ['title', 'body']
    ordering = ['-published_at', '-created_at']
    
    def get_attachment_count(self, obj):
        return obj.attachments.count()
    get_attachment_count.short_description = 'Attachments'


class NoticeAttachmentInline(admin.TabularInline):
    model = NoticeAttachment
    extra = 1
    readonly_fields = ['uploaded_at', 'file_size']
    fields = ['file', 'file_name', 'file_size', 'file_type', 'uploaded_at']


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['endpoint', 'is_active', 'updated_at', 'created_at']
    list_filter = ['is_active']
    search_fields = ['endpoint', 'user_agent']
    ordering = ['-updated_at']


@admin.register(NoticeAttachment)
class NoticeAttachmentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'notice', 'file_type', 'file_size_kb', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['file_name', 'notice__title']
    ordering = ['-uploaded_at']
    readonly_fields = ['uploaded_at', 'file_size', 'file_type']
    
    def file_size_kb(self, obj):
        return f"{obj.file_size / 1024:.1f} KB"
    file_size_kb.short_description = 'Size'


@admin.register(StudentMark)
class StudentMarkAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'semester', 'exam_type', 'exam_session', 'attempt_no', 'marks_obtained', 'max_marks', 'is_absent', 'updated_at']
    list_filter = ['exam_type', 'semester', 'is_absent']
    search_fields = ['student__enrollment_no', 'student__name', 'subject__code', 'exam_session']
    ordering = ['-updated_at']


@admin.register(MentorActionLog)
class MentorActionLogAdmin(admin.ModelAdmin):
    list_display = ['student', 'action_type', 'created_by', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['student__enrollment_no', 'student__name', 'note']
    ordering = ['-created_at']


@admin.register(MarksFreezeRule)
class MarksFreezeRuleAdmin(admin.ModelAdmin):
    list_display = ['semester', 'subject', 'exam_type', 'exam_session', 'attempt_no', 'is_frozen', 'frozen_by', 'frozen_at']
    list_filter = ['is_frozen', 'exam_type', 'semester']
    search_fields = ['subject__code', 'exam_session']
    ordering = ['-frozen_at']


@admin.register(MarksAuditTrail)
class MarksAuditTrailAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'exam_type', 'exam_session', 'attempt_no', 'action', 'changed_by', 'changed_at']
    list_filter = ['action', 'exam_type', 'semester']
    search_fields = ['student__enrollment_no', 'subject__code', 'reason', 'exam_session']
    ordering = ['-changed_at']


@admin.register(MentorAssignment)
class MentorAssignmentAdmin(admin.ModelAdmin):
    list_display = ['semester', 'division', 'faculty', 'assigned_at']
    list_filter = ['semester', 'division']
    search_fields = ['faculty__user__username', 'faculty__user__first_name', 'faculty__user__last_name']
    ordering = ['semester__number', 'division']

    def get_changeform_initial_data(self, request):
        # A class supports up to two mentors; enforced by model validation.
        return super().get_changeform_initial_data(request)
