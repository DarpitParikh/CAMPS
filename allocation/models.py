from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# ============= ACADEMIC STRUCTURE =============

class Branch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    
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
    max_marks = models.IntegerField(default=100, validators=[MinValueValidator(1)])
    internal_max = models.IntegerField(default=20)
    external_max = models.IntegerField(default=80)
    is_elective = models.BooleanField(default=False)
    
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
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

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
    ]
    
    enrollment_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    division = models.CharField(max_length=2, choices=DIVISION_CHOICES, default='A')
    mentor_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=10, blank=True)
    
    # Exam Seating Info
    exam_no = models.CharField(max_length=20, blank=True, null=True)
    room_no = models.CharField(max_length=10, blank=True, null=True)
    seat_no = models.IntegerField(blank=True, null=True)
    
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

# ============= MARKS =============

class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    internal = models.IntegerField(validators=[MinValueValidator(0)])
    external = models.IntegerField(validators=[MinValueValidator(0)])
    submitted = models.BooleanField(default=False)
    submitted_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ('student', 'subject')
        ordering = ['student__enrollment_no', 'subject__code']
    
    def get_total(self):
        return self.internal + self.external
    
    def get_grade(self):
        total = self.get_total()
        if total >= 90:
            return 'A+'
        elif total >= 80:
            return 'A'
        elif total >= 70:
            return 'B+'
        elif total >= 60:
            return 'B'
        elif total >= 50:
            return 'C'
        else:
            return 'F'
    
    def is_pass(self):
        return self.get_total() >= 40
    
    def __str__(self):
        return f"{self.student.enrollment_no} - {self.subject.code}"

# ============= EXAM SEATING (Existing Feature) =============

class CESeating(models.Model):
    room_no = models.CharField(max_length=10)
    seat_from = models.IntegerField()
    seat_to = models.IntegerField()
    count = models.IntegerField()
    
    def __str__(self):
        return f"Room {self.room_no} ({self.seat_from}-{self.seat_to})"
