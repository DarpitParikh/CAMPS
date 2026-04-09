from django import forms
from django.contrib.auth.models import User
from .models import Faculty, Student, Subject, Attendance, Branch, Semester, Notice
from datetime import date
import csv
import io


def _branch_option_label(branch):
    return branch.selection_label

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['branch'].label_from_instance = _branch_option_label

    class Meta:
        model = Student
        fields = ['enrollment_no', 'name', 'branch', 'semester', 'division', 'admission_year', 'mentor_name', 'email', 'phone']
        widgets = {
            'enrollment_no': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'division': forms.Select(attrs={'class': 'form-control'}),
            'admission_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '2000', 'max': '2100', 'placeholder': 'e.g. 2024'}),
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
    division = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
            ('E', 'E'),
            ('F', 'F'),
            ('G', 'G'),
            ('H', 'H'),
            ('I', 'I'),
        ],
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    mentor = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mentor name'
        })
    )
    admission_year = forms.IntegerField(
        required=False,
        min_value=2000,
        max_value=2100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Admission year'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Branch, Semester
        self.fields['branch'].queryset = Branch.objects.all()
        self.fields['branch'].label_from_instance = _branch_option_label
        self.fields['semester'].queryset = Semester.objects.all()

# ============= ATTENDANCE FORMS =============

class AttendanceForm(forms.Form):
    semester = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
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
    
    def __init__(self, *args, **kwargs):
        kwargs.pop('selected_semester_id', None)
        super().__init__(*args, **kwargs)
        self.fields['semester'].queryset = Semester.objects.all().order_by('number')
        self.fields['subject'].queryset = Subject.objects.select_related('semester').all().order_by('semester__number', 'code')

    def clean(self):
        cleaned_data = super().clean()
        semester = cleaned_data.get('semester')
        subject = cleaned_data.get('subject')
        if semester and subject and subject.semester_id != semester.id:
            self.add_error('subject', 'Selected subject does not belong to selected semester.')
        return cleaned_data

class StudentAttendanceForm(forms.Form):
    ATTENDANCE_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
    ]
    attendance = forms.ChoiceField(
        choices=ATTENDANCE_CHOICES,
        widget=forms.RadioSelect()
    )


class FacultyMarksEntryForm(forms.Form):
    EXAM_TYPE_CHOICES = [
        ('MID', 'Mid Semester'),
        ('FINAL', 'Final Exam'),
    ]

    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all().order_by('number'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    division = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'),
            ('E', 'E'), ('F', 'F'), ('G', 'G')
        ],
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    exam_type = forms.ChoiceField(
        choices=EXAM_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    exam_session = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. OCT 2026'})
    )
    attempt_no = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    max_marks = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        max_digits=6,
        initial=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'})
    )
    pass_marks = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        max_digits=6,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'placeholder': 'Optional'})
    )

    def __init__(self, *args, **kwargs):
        selected_semester_id = kwargs.pop('selected_semester_id', None)
        super().__init__(*args, **kwargs)
        subject_qs = Subject.objects.select_related('semester').all().order_by('semester__number', 'code')
        if selected_semester_id:
            subject_qs = subject_qs.filter(semester_id=selected_semester_id)
        self.fields['subject'].queryset = subject_qs

# ============= EXAM SEATING FORM (EXISTING) =============

class CEForm(forms.Form):
    examination_name = forms.CharField(label="Examination Name", required=False, help_text="E.g., Continuous Evaluation, Mid Semester, etc.")
    semester = forms.IntegerField(label="Semester")
    month = forms.CharField(label="Month", initial="NOVEMBER")
    year = forms.IntegerField(label="Year", initial=2025)
    date_from = forms.CharField(label="Date From", initial="07-11-2025", help_text="Format: DD-MM-YYYY")
    date_to = forms.CharField(label="Date To", initial="11-11-2025", help_text="Format: DD-MM-YYYY")
    
    start_exam_no = forms.IntegerField(label="Starting Exam No", help_text="Starting exam number for students")
    
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['branch'].label_from_instance = _branch_option_label

    class Meta:
        model = Subject
        fields = ['code', 'name', 'branch', 'semester', 'credit', 'is_elective', 'elective_group']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'is_elective': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'elective_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ELECTIVE-I'}),
        }


# ============= STUDENT UPLOAD =============

class StudentUploadForm(forms.Form):
    branch = forms.ModelChoiceField(queryset=Branch.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    semester = forms.ModelChoiceField(queryset=Semester.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls,.csv'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['branch'].label_from_instance = _branch_option_label

# ============= RESULT/ MARKSHEET FORMS =============

class MarksheetUploadForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls,.csv'})
    )

class ResultLookupForm(forms.Form):
    enrollment_no = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enrollment Number'})
    )
    semester = forms.IntegerField(
        min_value=1,
        max_value=8,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Semester'})
    )


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['notice_type', 'title', 'body', 'is_published']
        widgets = {
            'notice_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter notice title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write details for students...'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


