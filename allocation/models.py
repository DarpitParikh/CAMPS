from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

# ============= ACADEMIC STRUCTURE =============

class Branch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    @property
    def selection_label(self):
        clean_name = (self.name or '').strip()
        clean_code = (self.code or '').strip()
        if not clean_name:
            return clean_code
        if not clean_code:
            return clean_name
        if clean_name.casefold() in {'civil', 'civil engineering'}:
            return clean_name
        return f"{clean_name} ({clean_code})"
    
    def __str__(self):
        return self.name

class Semester(models.Model):
    number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    
    class Meta:
        ordering = ['number']
    
    def __str__(self):
        return f"Semester {self.number}"

class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    credit = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_elective = models.BooleanField(default=False)
    elective_group = models.CharField(max_length=50, blank=True)
    
    class Meta:
        unique_together = ('code', 'branch', 'semester')
        ordering = ['semester', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

# ============= FACULTY MANAGEMENT =============

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    subjects = models.ManyToManyField(Subject, related_name='faculty_teachers')
    last_subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL, related_name='last_used_by')
    last_semester = models.ForeignKey(Semester, null=True, blank=True, on_delete=models.SET_NULL)
    must_change_password = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"


class MentorAssignment(models.Model):
    DIVISION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
        ('G', 'G'),
    ]

    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='mentor_assignments')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    division = models.CharField(max_length=2, choices=DIVISION_CHOICES)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('faculty', 'semester', 'division')
        ordering = ['semester__number', 'division']

    def __str__(self):
        return f"Sem {self.semester.number} - Div {self.division} -> {self.faculty.user.username}"

    def clean(self):
        qs = MentorAssignment.objects.filter(semester=self.semester, division=self.division)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.count() >= 2:
            raise ValidationError('A class can have at most two mentors.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

# ============= STUDENT MANAGEMENT =============

class Student(models.Model):
    BRANCH_CHOICES = [
        ('CE', 'Civil Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('EC', 'Electronics & Communication'),
        ('EE', 'Electrical Engineering'),
        ('CS', 'Computer Science'),
    ]
    DIVISION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
        ('G', 'G'),
    ]
    
    enrollment_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    division = models.CharField(max_length=2, choices=DIVISION_CHOICES, default='A')
    admission_year = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(2000), MaxValueValidator(2100)]
    )
    mentor_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=10, blank=True)
    
    # Exam Seating Info
    exam_no = models.CharField(max_length=20, blank=True, null=True)
    room_no = models.CharField(max_length=10, blank=True, null=True)
    
    class Meta:
        ordering = ['enrollment_no']
    
    def __str__(self):
        return f"{self.enrollment_no} - {self.name}"

class StudentSubject(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subjects_enrolled')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('student', 'subject')
    
    def __str__(self):
        return f"{self.student.enrollment_no} - {self.subject.code}"

# ============= ATTENDANCE =============

class Attendance(models.Model):
    ATTENDANCE_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=1, choices=ATTENDANCE_CHOICES, default='P')
    marked_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ('student', 'subject', 'date')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.enrollment_no} - {self.subject.code} - {self.date} ({self.status})"

# ============= EXAM SEATING (Existing Feature) =============

class CESeating(models.Model):
    room_no = models.CharField(max_length=10)
    seat_from = models.IntegerField()
    seat_to = models.IntegerField()
    count = models.IntegerField()
    
    def __str__(self):
        return f"Room {self.room_no} ({self.seat_from}-{self.seat_to})"

# ============= RESULTS / MARKSHEETS =============

class ResultSheet(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='result_sheets')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    exam_session = models.CharField(max_length=50)  # e.g., APRIL 2025
    issued_date = models.DateField(null=True, blank=True)
    spi = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    cpi = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    earned_credits = models.IntegerField(null=True, blank=True)
    earned_grade_points = models.IntegerField(null=True, blank=True)
    total_credits = models.IntegerField(null=True, blank=True)
    total_grade_points = models.IntegerField(null=True, blank=True)
    result_status = models.CharField(max_length=20, default='PASS')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'semester', 'exam_session')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.enrollment_no} - Sem {self.semester.number}"

class ResultEntry(models.Model):
    result_sheet = models.ForeignKey(ResultSheet, on_delete=models.CASCADE, related_name='entries')
    course_code = models.CharField(max_length=30)
    course_name = models.CharField(max_length=200)
    course_credit = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5)

    class Meta:
        ordering = ['course_code']

    def __str__(self):
        return f"{self.course_code} - {self.grade}"


class StudentMark(models.Model):
    EXAM_TYPE_CHOICES = [
        ('MID', 'Mid Semester'),
        ('FINAL', 'Final Exam'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='marks_records')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES)
    exam_session = models.CharField(max_length=50)  # e.g., OCT 2026
    attempt_no = models.PositiveIntegerField(default=1)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    pass_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_absent = models.BooleanField(default=False)
    entered_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    entered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'subject', 'exam_type', 'exam_session', 'attempt_no')
        ordering = ['-updated_at', 'student__enrollment_no']

    def __str__(self):
        return f"{self.student.enrollment_no} - {self.subject.code} ({self.exam_type} {self.exam_session} A{self.attempt_no})"


class MarksFreezeRule(models.Model):
    EXAM_TYPE_CHOICES = StudentMark.EXAM_TYPE_CHOICES

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES)
    exam_session = models.CharField(max_length=50)
    attempt_no = models.PositiveIntegerField(default=1)
    is_frozen = models.BooleanField(default=True)
    note = models.CharField(max_length=250, blank=True)
    frozen_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    frozen_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('semester', 'subject', 'exam_type', 'exam_session', 'attempt_no')
        ordering = ['-frozen_at']

    def __str__(self):
        state = 'Frozen' if self.is_frozen else 'Open'
        return f"{self.subject.code} {self.exam_type} {self.exam_session} A{self.attempt_no} [{state}]"


class MarksAuditTrail(models.Model):
    ACTION_CHOICES = [
        ('UPDATE', 'Update'),
        ('FREEZE', 'Freeze'),
        ('UNFREEZE', 'Unfreeze'),
    ]

    student_mark = models.ForeignKey(StudentMark, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=10, choices=StudentMark.EXAM_TYPE_CHOICES)
    exam_session = models.CharField(max_length=50)
    attempt_no = models.PositiveIntegerField(default=1)

    old_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    new_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    old_absent = models.BooleanField(default=False)
    new_absent = models.BooleanField(default=False)
    old_max_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    new_max_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    old_pass_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    new_pass_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    reason = models.CharField(max_length=300, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='UPDATE')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.student.enrollment_no} {self.subject.code} {self.exam_type} {self.exam_session}"


class MentorActionLog(models.Model):
    ACTION_CHOICES = [
        ('MEETING', 'Counselling Meeting'),
        ('CALL', 'Parent Call'),
        ('REMEDIAL', 'Remedial Assigned'),
        ('WARNING', 'Warning Given'),
        ('OTHER', 'Other'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='mentor_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, default='OTHER')
    note = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.enrollment_no} - {self.get_action_type_display()}"


class Notice(models.Model):
    NOTICE_TYPE_CHOICES = [
        ('NOTICE', 'Notice'),
        ('RESULT', 'Result'),
    ]

    notice_type = models.CharField(max_length=10, choices=NOTICE_TYPE_CHOICES, default='NOTICE')
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    source_key = models.CharField(max_length=80, unique=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return f"{self.get_notice_type_display()} - {self.title}"


class PushSubscription(models.Model):
    endpoint = models.URLField(unique=True)
    p256dh = models.TextField()
    auth = models.TextField()
    user_agent = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.endpoint[:80]


class NoticeAttachment(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='notice_attachments/%Y/%m/%d/')
    file_name = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=50, blank=True)  # e.g., 'pdf', 'image', 'document'
    file_size = models.BigIntegerField(default=0)  # in bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Notice Attachment'
        verbose_name_plural = 'Notice Attachments'

    def __str__(self):
        return f"{self.file_name or self.file.name} - {self.notice.title}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            # Auto-set file_name and detect type
            if not self.file_name:
                self.file_name = self.file.name.split('/')[-1]
            # Detect file type by extension
            ext = self.file_name.split('.')[-1].lower() if '.' in self.file_name else ''
            if ext in ['pdf']:
                self.file_type = 'pdf'
            elif ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                self.file_type = 'image'
            elif ext in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']:
                self.file_type = 'document'
            else:
                self.file_type = ext or 'file'
        super().save(*args, **kwargs)



