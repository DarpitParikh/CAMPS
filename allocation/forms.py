from django import forms
from django.contrib.auth.models import User
from .models import Faculty, Student, Subject, Marks, Attendance, Branch, Semester
from datetime import date
import csv
import io

# ============= AUTHENTICATION FORMS =============

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

# ============= STUDENT FORMS =============

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['enrollment_no', 'name', 'branch', 'semester', 'division', 'mentor_name', 'email', 'phone']
        widgets = {
            'enrollment_no': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'division': forms.Select(attrs={'class': 'form-control'}),
            'mentor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}),
        }

class StudentSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name or enrollment...'
        })
    )
    branch = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    semester = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    division = forms.ChoiceField(
        required=False,
        choices=[('', 'All'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    mentor = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mentor name'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Branch, Semester
        self.fields['branch'].queryset = Branch.objects.all()
        self.fields['semester'].queryset = Semester.objects.all()

# ============= ATTENDANCE FORMS =============

class AttendanceForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        initial=date.today(),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def __init__(self, faculty, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = faculty.subjects.all()

class StudentAttendanceForm(forms.Form):
    ATTENDANCE_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
    ]
    attendance = forms.ChoiceField(
        choices=ATTENDANCE_CHOICES,
        widget=forms.RadioSelect()
    )

# ============= MARKS FORMS =============

class MarksForm(forms.ModelForm):
    class Meta:
        model = Marks
        fields = ['internal', 'external']
        widgets = {
            'internal': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'external': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
    
    def __init__(self, subject, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subject = subject
        self.fields['internal'].widget.attrs['max'] = subject.internal_max
        self.fields['external'].widget.attrs['max'] = subject.external_max

class MarksEntryForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, faculty, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = faculty.subjects.all()

# ============= EXAM SEATING FORM (EXISTING) =============

class CEForm(forms.Form):
    semester = forms.IntegerField(label="Semester")
    month = forms.CharField(label="Month", initial="NOVEMBER")
    year = forms.IntegerField(label="Year", initial=2025)
    date_from = forms.CharField(label="Date From", initial="07-11-2025", help_text="Format: DD-MM-YYYY")
    date_to = forms.CharField(label="Date To", initial="11-11-2025", help_text="Format: DD-MM-YYYY")
    
    start_exam_no = forms.IntegerField(label="Starting Exam No", help_text="Starting exam number for students")
    student_file = forms.FileField(
        label="Upload Student List (Excel/CSV)",
        required=False,
        help_text="Upload Excel or CSV file with columns: Enrollment No, Student Name"
    )
    
    start_seat = forms.IntegerField(label="Starting Seat No")
    total_students = forms.IntegerField(label="Total Students")
    preferred_per_room = forms.IntegerField(label="Preferred Students per Room", initial=31)
    max_per_room = forms.IntegerField(label="Maximum Allowed per Room", initial=36)
    rooms = forms.CharField(
        label="Available Rooms",
        widget=forms.Textarea(attrs={'rows': 2}),
        help_text="Example: 301-305,307,401-403"
    )
    note = forms.CharField(
        label="Note (Optional)",
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
    )

# ============= EXCEL UPLOAD FORM =============

class ExcelUploadForm(forms.Form):
    UPLOAD_TYPE_CHOICES = [
        ('students', 'Student List'),
        ('marks', 'Student Marks'),
        ('attendance', 'Attendance Records'),
    ]
    
    upload_type = forms.ChoiceField(
        choices=UPLOAD_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls,.csv'})
    )
    subject = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, faculty=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if faculty:
            self.fields['subject'].queryset = faculty.subjects.all()

# ============= SUBJECT MANAGEMENT =============

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['code', 'name', 'branch', 'semester', 'internal_max', 'external_max']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'internal_max': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'mentor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Dr. Sharma'}),
        }

    def clean(self):
        cleaned = super().clean()
        internal = cleaned.get('internal_max') or 0
        external = cleaned.get('external_max') or 0
        if internal + external <= 0:
            raise forms.ValidationError('Total marks must be greater than 0.')
        return cleaned


# ============= STUDENT UPLOAD =============

class StudentUploadForm(forms.Form):
    branch = forms.ModelChoiceField(queryset=Branch.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    semester = forms.ModelChoiceField(queryset=Semester.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls,.csv'}))

