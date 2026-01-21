from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q, Avg
from django.views.decorators.http import require_POST
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # type: ignore
from reportlab.lib.units import inch
from reportlab.lib import colors
from .forms import CEForm, StudentForm, StudentSearchForm, AttendanceForm, ExcelUploadForm, SubjectForm, StudentUploadForm
from .models import (
    CESeating, Student, Faculty, Subject, Semester, Branch,
    Attendance, Marks, StudentSubject
)
import pandas as pd
import io
from datetime import datetime, timedelta

def parse_rooms(room_text):
    rooms = []
    seen = set()

    for part in room_text.split(','):
        part = part.strip()

        if '-' in part:
            start, end = part.split('-')
            for r in range(int(start), int(end) + 1):
                room = str(r)
                if room not in seen:
                    rooms.append(room)
                    seen.add(room)
        else:
            if part and part not in seen:
                rooms.append(part)
                seen.add(part)

    return rooms

from datetime import datetime, timedelta

# ============= DASHBOARD VIEWS =============

@login_required(login_url='login')
def dashboard(request):
    """Main dashboard - redirects based on role"""
    if request.user.is_staff:
        return admin_dashboard(request)
    elif hasattr(request.user, 'faculty'):
        return faculty_dashboard(request)
    else:
        # Break redirect loop: show simple access message instead of redirecting
        return render(request, 'auth/login.html', {
            'form': None,
            'error': 'Your account is not assigned a role. Please contact admin.'
        })

def admin_dashboard(request):
    """Admin (Exam Cell) Dashboard"""
    total_students = Student.objects.count()
    total_subjects = Subject.objects.count()
    total_faculty = Faculty.objects.count()
    
    # Latest activities
    recent_marks = Marks.objects.filter(submitted=True).order_by('-submitted_date')[:5]
    recent_attendance = Attendance.objects.order_by('-date')[:5]
    
    context = {
        'total_students': total_students,
        'total_subjects': total_subjects,
        'total_faculty': total_faculty,
        'recent_marks': recent_marks,
        'recent_attendance': recent_attendance,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

def faculty_dashboard(request):
    """Faculty Dashboard"""
    try:
        faculty = request.user.faculty
    except:
        return redirect('login')
    
    subjects = faculty.subjects.all()
    
    # Get last accessed subject/semester
    last_subject = faculty.last_subject
    last_semester = faculty.last_semester
    
    # Pending work indicators
    pending_attendance = {}
    
    for subject in subjects:
        # Check attendance
        today = timezone.now().date()
        today_attendance = Attendance.objects.filter(
            subject=subject,
            date=today,
            marked_by=faculty
        ).count()
        
        if today_attendance == 0:
            pending_attendance[subject.id] = 'Not marked today'
        
        # Marks entry removed from system
    
    context = {
        'faculty': faculty,
        'subjects': subjects,
        'last_subject': last_subject,
        'last_semester': last_semester,
        'pending_attendance': pending_attendance,
        # 'pending_marks' removed
    }
    return render(request, 'dashboard/faculty_dashboard.html', context)

# ============= STUDENT MANAGEMENT =============

@login_required(login_url='login')
def student_list(request):
    """List and search students"""
    # Allow both admin and faculty to view students
    
    form = StudentSearchForm(request.GET)
    students = Student.objects.all()
    
    if request.GET:
        query = request.GET.get('query', '')
        branch = request.GET.get('branch')
        semester = request.GET.get('semester')
        division = request.GET.get('division')
        mentor = request.GET.get('mentor')
        sort = request.GET.get('sort', '')
        order = request.GET.get('order', 'asc')
        
        if query:
            students = students.filter(
                Q(name__icontains=query) |
                Q(enrollment_no__icontains=query)
            )
        
        if branch:
            students = students.filter(branch_id=branch)
        
        if semester:
            students = students.filter(semester_id=semester)

        if division:
            students = students.filter(division=division)

        if mentor:
            students = students.filter(mentor_name__icontains=mentor)

        # Sorting
        sort_map = {
            'name': 'name',
            'enrollment_no': 'enrollment_no',
            'branch': 'branch__name',
            'semester': 'semester__number',
            'division': 'division',
            'mentor': 'mentor_name',
        }
        sort_field = sort_map.get(sort, 'enrollment_no')
        if order == 'desc':
            sort_field = '-' + sort_field
        students = students.order_by(sort_field)
    
    context = {
        'students': students,
        'form': form,
    }
    return render(request, 'students/student_list.html', context)

@login_required(login_url='login')
def student_profile(request, student_id):
    """Student Profile Page - shows complete academic information"""
    student = get_object_or_404(Student, id=student_id)
    
    # Basic info already in student object
    
    # Get enrolled subjects
    enrolled_subjects = StudentSubject.objects.filter(student=student).select_related('subject')
    
    # Get attendance records
    attendance_summary = {}
    for subject_enrollment in enrolled_subjects:
        subject = subject_enrollment.subject
        total_classes = Attendance.objects.filter(subject=subject).count()
        present_count = Attendance.objects.filter(
            student=student,
            subject=subject,
            status='P'
        ).count()
        
        percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
        attendance_summary[subject.code] = {
            'present': present_count,
            'total': total_classes,
            'percentage': round(percentage, 1)
        }
    
    # Get marks summary
    marks_data = Marks.objects.filter(student=student).select_related('subject')
    marks_summary = {}
    total_marks = 0
    total_max = 0
    
    for mark in marks_data:
        marks_summary[mark.subject.code] = {
            'internal': mark.internal,
            'external': mark.external,
            'total': mark.get_total(),
            'max': mark.subject.max_marks,
            'grade': mark.get_grade(),
            'pass': mark.is_pass(),
        }
        total_marks += mark.get_total()
        total_max += mark.subject.max_marks
    
    context = {
        'student': student,
        'enrolled_subjects': enrolled_subjects,
        'attendance_summary': attendance_summary,
        'marks_summary': marks_summary,
        'total_marks': total_marks,
        'total_max': total_max,
        'overall_percentage': round(total_marks / total_max * 100, 1) if total_max > 0 else 0,
    }
    return render(request, 'students/student_profile.html', context)

@login_required(login_url='login')
def add_student(request):
    """Add new student (Admin only)"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm()
    
    context = {'form': form}
    return render(request, 'students/add_student.html', context)

@login_required(login_url='login')
def delete_student(request, student_id):
    """Delete a student (Admin only) with confirmation."""
    if not request.user.is_staff:
        return redirect('dashboard')

    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        confirm = request.POST.get('confirm_enrollment', '').strip()
        if confirm != student.enrollment_no:
            return render(request, 'students/confirm_delete.html', {
                'student': student,
                'error': 'Enrollment number does not match. Deletion cancelled.'
            })
        # Cascade deletes will handle related records
        student.delete()
        return redirect('student_list')

    return render(request, 'students/confirm_delete.html', {
        'student': student
    })

# ============= ATTENDANCE VIEWS =============

@login_required(login_url='login')
def mark_attendance(request):
    """Mark daily attendance"""
    try:
        faculty = request.user.faculty
    except:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AttendanceForm(faculty, request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            date = form.cleaned_data['date']
            
            # Update faculty context
            faculty.last_subject = subject
            faculty.save()
            
            # Get students enrolled in this subject
            student_enrollments = StudentSubject.objects.filter(subject=subject)
            
            # Process attendance from POST data
            for enrollment in student_enrollments:
                student = enrollment.student
                status_key = f'student_{student.id}'
                status = request.POST.get(status_key, 'P')
                
                # Update or create attendance record
                Attendance.objects.update_or_create(
                    student=student,
                    subject=subject,
                    date=date,
                    defaults={
                        'status': status,
                        'marked_by': faculty
                    }
                )
            
            return redirect('mark_attendance')
    else:
        form = AttendanceForm(faculty)
    
    # If subject and date are selected, show student list
    subject = request.GET.get('subject')
    date = request.GET.get('date')
    division = request.GET.get('division')
    students = []
    current_attendance = {}
    
    if subject and date:
        try:
            subject_obj = Subject.objects.get(id=subject)
            student_enrollments = StudentSubject.objects.filter(subject=subject_obj).select_related('student')
            
            # Filter by division if specified
            if division:
                student_enrollments = student_enrollments.filter(student__division=division)
            
            students = [enrollment.student for enrollment in student_enrollments]
            
            # Get current attendance records
            records = Attendance.objects.filter(subject=subject_obj, date=date)
            if division:
                records = records.filter(student__division=division)
            current_attendance = {record.student_id: record.status for record in records}
        except:
            pass
    
    context = {
        'form': form,
        'students': students,
        'current_attendance': current_attendance,
        'date': date,
        'subject': subject,
    }
    return render(request, 'attendance/mark_attendance.html', context)

# ============= MARKS VIEWS REMOVED =============

# ============= EXAM SEATING (EXISTING) =============

def parse_rooms(room_text):
    rooms = []
    seen = set()
    for part in room_text.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            for r in range(int(start), int(end) + 1):
                room = str(r)
                if room not in seen:
                    rooms.append(room)
                    seen.add(room)
        else:
            if part and part not in seen:
                rooms.append(part)
                seen.add(part)
    return rooms

@login_required(login_url='login')
def allocate(request):
    """Exam seating allocation (Admin only)"""
    # Allow faculty to generate seating as requested
    
    if request.method == "POST":
        form = CEForm(request.POST, request.FILES)
        if form.is_valid():
            CESeating.objects.all().delete()
            
            semester = form.cleaned_data['semester']
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            note = form.cleaned_data.get('note', '')
            start_exam_no = form.cleaned_data['start_exam_no']
            seat = form.cleaned_data['start_seat']
            total = form.cleaned_data['total_students']
            preferred = form.cleaned_data['preferred_per_room']
            max_limit = form.cleaned_data['max_per_room']
            
            rooms = parse_rooms(form.cleaned_data['rooms'])
            room_count = len(rooms)
            
            # Capacity Check
            if total > room_count * max_limit:
                return HttpResponse("ERROR: Not enough rooms. Please add more rooms.", status=400)
            
            # Smart Allocation Logic
            room_allocations = [preferred] * room_count
            remaining = total - (preferred * room_count)
            
            if remaining > 0:
                for i in range(room_count - 1, -1, -1):
                    if remaining <= 0:
                        break
                    can_add = min(remaining, max_limit - preferred)
                    room_allocations[i] += can_add
                    remaining -= can_add
            
            if remaining > 0:
                return HttpResponse("ERROR: Cannot allocate all students. Increase max per room or add more rooms.", status=400)
            
            # Create seating records
            seat_no = seat
            for i, room in enumerate(rooms):
                count = room_allocations[i]
                start = seat_no
                end = seat_no + count - 1
                
                CESeating.objects.create(
                    room_no=room,
                    seat_from=start,
                    seat_to=end,
                    count=count
                )
                seat_no = end + 1
            
            from urllib.parse import urlencode
            params = urlencode({
                'semester': semester,
                'month': month,
                'year': year,
                'date_from': date_from,
                'date_to': date_to,
                'note': note
            })
            return redirect(f"/preview/?{params}")
    else:
        form = CEForm()
    
    return render(request, "allocate.html", {"form": form})

# ============= ADMIN HELPERS =============

@login_required(login_url='login')
def manage_roles(request):
    """Admin page to assign faculty roles to users and seed a demo faculty user."""
    if not request.user.is_staff:
        return redirect('dashboard')

    # Users without a faculty profile
    users_without_faculty = User.objects.filter(faculty__isnull=True).order_by('username')
    subjects = Subject.objects.all().order_by('code')

    message = None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'assign':
            user_id = request.POST.get('user_id')
            employee_id = request.POST.get('employee_id')
            subject_ids = request.POST.getlist('subjects')
            try:
                target_user = User.objects.get(id=user_id)
                faculty, created = Faculty.objects.get_or_create(user=target_user, defaults={
                    'employee_id': employee_id or f'EMP{target_user.id:04d}'
                })
                if not created and employee_id:
                    faculty.employee_id = employee_id
                    faculty.save()
                if subject_ids:
                    faculty.subjects.set(Subject.objects.filter(id__in=subject_ids))
                message = f"Assigned faculty role to {target_user.username}."
            except User.DoesNotExist:
                message = "Selected user does not exist."
        elif action == 'seed_demo':
            # Create a demo faculty user and link a faculty profile
            demo_username = 'faculty1'
            demo_password = 'faculty123'
            demo_email = 'faculty1@example.com'
            target_user, created = User.objects.get_or_create(username=demo_username, defaults={
                'email': demo_email
            })
            if created:
                target_user.set_password(demo_password)
                target_user.save()
            faculty, fac_created = Faculty.objects.get_or_create(user=target_user, defaults={
                'employee_id': 'EMP0001'
            })
            if subjects.exists():
                # Assign first subject by default to make dashboards work
                faculty.subjects.add(subjects.first())
            message = "Demo faculty user created: username 'faculty1', password 'faculty123'."

        # Refresh lists after changes
        users_without_faculty = User.objects.filter(faculty__isnull=True).order_by('username')

    context = {
        'users_without_faculty': users_without_faculty,
        'subjects': subjects,
        'message': message,
    }
    return render(request, 'admin/manage_roles.html', context)

@login_required(login_url='login')
def assign_subjects(request):
    """Admin page to assign subjects to faculty users with filters."""
    if not request.user.is_staff:
        return redirect('dashboard')

    faculties = Faculty.objects.select_related('user').order_by('user__username')
    branches = Branch.objects.all().order_by('name')
    semesters = Semester.objects.all().order_by('number')

    faculty_id = request.GET.get('faculty') or request.POST.get('faculty')
    branch_id = request.GET.get('branch') or request.POST.get('branch')
    semester_id = request.GET.get('semester') or request.POST.get('semester')

    selected_faculty = None
    subjects = Subject.objects.none()
    assigned_ids = set()
    message = None

    if faculty_id:
        selected_faculty = get_object_or_404(Faculty, id=faculty_id)

        # Filter subjects optionally by branch and semester
        subj_qs = Subject.objects.all()
        if branch_id:
            subj_qs = subj_qs.filter(branch_id=branch_id)
        if semester_id:
            subj_qs = subj_qs.filter(semester_id=semester_id)
        subjects = subj_qs.order_by('code')

        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'save_assignments':
                selected_subject_ids = [int(sid) for sid in request.POST.getlist('subjects')]
                # Only consider subjects visible in current filter for update set/add/remove
                visible_ids = list(subjects.values_list('id', flat=True))
                current_set = set(selected_faculty.subjects.values_list('id', flat=True))

                # Add newly selected among visible
                to_add = set(selected_subject_ids) - current_set
                if to_add:
                    selected_faculty.subjects.add(*Subject.objects.filter(id__in=to_add))

                # Remove deselected among visible
                to_remove = (current_set & set(visible_ids)) - set(selected_subject_ids)
                if to_remove:
                    selected_faculty.subjects.remove(*Subject.objects.filter(id__in=to_remove))

                message = 'Assignments updated.'

        assigned_ids = set(selected_faculty.subjects.values_list('id', flat=True))

    context = {
        'faculties': faculties,
        'branches': branches,
        'semesters': semesters,
        'selected_faculty': selected_faculty,
        'subjects': subjects,
        'assigned_ids': assigned_ids,
        'branch_id': branch_id,
        'semester_id': semester_id,
        'message': message,
    }
    return render(request, 'admin/assign_subjects.html', context)

# ============= SUBJECTS BY SEMESTER =============

@login_required(login_url='login')
def manage_subjects(request):
    """Admin page to list subjects by branch/semester and add new ones."""
    if not request.user.is_staff:
        return redirect('dashboard')

    selected_branch_id = request.GET.get('branch')
    selected_semester_id = request.GET.get('semester')

    branches = Branch.objects.all().order_by('name')
    semesters = Semester.objects.all().order_by('number')

    subjects = Subject.objects.none()
    if selected_branch_id and selected_semester_id:
        subjects = Subject.objects.filter(branch_id=selected_branch_id, semester_id=selected_semester_id).order_by('code')

    message = None

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.max_marks = (subject.internal_max or 0) + (subject.external_max or 0)
            subject.save()
            message = f"Subject {subject.code} added."
            # Update listing to include the newly added subject
            selected_branch_id = subject.branch_id
            selected_semester_id = subject.semester_id
            subjects = Subject.objects.filter(branch=subject.branch, semester=subject.semester).order_by('code')
            form = SubjectForm()
        else:
            message = "Please correct the errors below."
    else:
        form = SubjectForm()

    context = {
        'branches': branches,
        'semesters': semesters,
        'subjects': subjects,
        'selected_branch_id': selected_branch_id,
        'selected_semester_id': selected_semester_id,
        'form': form,
        'message': message,
    }
    return render(request, 'subjects/manage_subjects.html', context)


# ============= STUDENT UPLOAD =============

@login_required(login_url='login')
def upload_students(request):
    """Upload a sheet (CSV/XLSX) of students and bulk insert into a selected branch+semester."""
    if not request.user.is_staff:
        return redirect('dashboard')

    message = None
    results = None
    preview_rows = None

    if request.method == 'POST':
        form = StudentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            branch = form.cleaned_data['branch']
            semester = form.cleaned_data['semester']
            f = form.cleaned_data['file']

            # Read file using pandas
            try:
                if str(f.name).lower().endswith('.csv'):
                    df = pd.read_csv(f)
                else:
                    df = pd.read_excel(f)
            except Exception as e:
                message = f"Failed to read file: {e}"
                df = None

            if df is not None:
                # Normalize column names
                df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]

                # Map common variants
                colmap = {
                    'enrollment_no': ['enrollment_no', 'enrollment', 'enrollment_number', 'enrollmentno'],
                    'name': ['name', 'student_name', 'fullname'],
                    'division': ['division', 'div'],
                    'mentor_name': ['mentor_name', 'mentor', 'class_teacher'],
                    'email': ['email', 'mail'],
                    'phone': ['phone', 'mobile', 'contact']
                }

                resolved = {}
                for target, variants in colmap.items():
                    for v in variants:
                        if v in df.columns:
                            resolved[target] = v
                            break

                required_missing = [k for k in ['enrollment_no', 'name'] if k not in resolved]
                if required_missing:
                    message = f"Missing required columns: {', '.join(required_missing)}."
                else:
                    # Prepare rows
                    rows = []
                    errors = []
                    for i, row in df.iterrows():
                        enroll = str(row[resolved['enrollment_no']]).strip()
                        name = str(row[resolved['name']]).strip()
                        division = str(row[resolved.get('division', '')]).strip() if resolved.get('division') else ''
                        mentor_name = str(row[resolved.get('mentor_name', '')]).strip() if resolved.get('mentor_name') else ''
                        email = str(row[resolved.get('email', '')]) if resolved.get('email') else ''
                        phone = str(row[resolved.get('phone', '')]) if resolved.get('phone') else ''

                        if not enroll or not name:
                            errors.append(f"Row {i+1}: missing required fields")
                            continue

                        rows.append({
                            'enrollment_no': enroll,
                            'name': name,
                            'division': division or 'A',
                            'mentor_name': mentor_name,
                            'email': email,
                            'phone': phone,
                        })

                    # Insert records (skip duplicates)
                    created = 0
                    skipped = 0
                    for r in rows:
                        if Student.objects.filter(enrollment_no=r['enrollment_no']).exists():
                            skipped += 1
                            continue
                        Student.objects.create(
                            enrollment_no=r['enrollment_no'],
                            name=r['name'],
                            division=r['division'],
                            mentor_name=r['mentor_name'],
                            email=r['email'],
                            phone=r['phone'],
                            branch=branch,
                            semester=semester,
                        )
                        created += 1

                    results = {
                        'created': created,
                        'skipped': skipped,
                        'errors': errors,
                        'total': len(rows)
                    }
                    preview_rows = rows[:20]
                    message = f"Upload complete: {created} created, {skipped} skipped."
        else:
            message = "Please select branch, semester and a valid file."
    else:
        form = StudentUploadForm()

    return render(request, 'students/upload_students.html', {
        'form': form,
        'message': message,
        'results': results,
        'preview_rows': preview_rows,
    })


# ============= ENROLLMENTS (TOGGLES) =============

@login_required(login_url='login')
def manage_enrollments(request):
    """Toggle subject enrollments per student for a branch+semester.
    Also supports bulk assigning all non-elective subjects to all students."""
    if not request.user.is_staff:
        return redirect('dashboard')

    branches = Branch.objects.all().order_by('name')
    semesters = Semester.objects.all().order_by('number')

    branch_id = request.GET.get('branch') or request.POST.get('branch')
    semester_id = request.GET.get('semester') or request.POST.get('semester')
    division = request.GET.get('division') or request.POST.get('division')

    students = []
    subjects = []
    message = None

    if branch_id and semester_id:
        qs = Student.objects.filter(branch_id=branch_id, semester_id=semester_id)
        if division:
            qs = qs.filter(division=division)
        students = list(qs.order_by('enrollment_no'))
        subjects = list(Subject.objects.filter(branch_id=branch_id, semester_id=semester_id).order_by('code'))

        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'bulk_assign_fixed':
                fixed_subjects = [s for s in subjects if not s.is_elective]
                created = 0
                for stu in students:
                    for subj in fixed_subjects:
                        obj, was_created = StudentSubject.objects.get_or_create(student=stu, subject=subj)
                        if was_created:
                            created += 1
                message = f"Assigned {created} enrollments for fixed subjects."
            elif action == 'save_toggles':
                # Update per checkbox
                # Checkbox names: enroll_<student_id>_<subject_id>
                selected = set()
                for key in request.POST.keys():
                    if key.startswith('enroll_'):
                        _, sid, subid = key.split('_')
                        selected.add((int(sid), int(subid)))

                # Ensure selected ones exist, remove non-selected
                existing = set(StudentSubject.objects.filter(student__in=students, subject__in=subjects)
                               .values_list('student_id', 'subject_id'))

                # Create missing selected
                to_create = selected - existing
                for sid, subid in to_create:
                    StudentSubject.objects.get_or_create(student_id=sid, subject_id=subid)

                # Delete deselected
                to_delete = existing - selected
                if to_delete:
                    StudentSubject.objects.filter(student_id__in=[sid for sid, _ in to_delete],
                                                  subject_id__in=[subid for _, subid in to_delete]).delete()
                message = "Enrollments updated."

        # Refresh after changes: build map of student_id -> list of subject_ids
        pairs = StudentSubject.objects.filter(student__in=students, subject__in=subjects)
        pairs = pairs.values_list('student_id', 'subject_id')
        enroll_map = {}
        for sid, subid in pairs:
            enroll_map.setdefault(sid, []).append(subid)
    else:
        enroll_map = {}

    context = {
        'branches': branches,
        'semesters': semesters,
        'students': students,
        'subjects': subjects,
        'branch_id': branch_id,
        'semester_id': semester_id,
        'division': division,
        'enroll_map': enroll_map,
        'message': message,
    }
    return render(request, 'subjects/manage_enrollments.html', context)

@login_required(login_url='login')
def preview(request):
    """Preview exam seating"""
    seating = CESeating.objects.all()
    context = {
        "seating": seating,
        "semester": request.GET.get("semester", ""),
        "month": request.GET.get("month", "NOVEMBER"),
        "year": request.GET.get("year", "2025"),
        "date_from": request.GET.get("date_from", ""),
        "date_to": request.GET.get("date_to", ""),
        "note": request.GET.get("note", "")
    }
    return render(request, "preview.html", context)

@login_required(login_url='login')
def download_pdf(request):
    """Download exam seating PDF"""
    # Allow faculty to download seating PDF
    
    semester = request.GET.get("semester", "")
    month = request.GET.get("month", "NOVEMBER")
    year = request.GET.get("year", "2025")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    note = request.GET.get("note", "")
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="CE_Seating.pdf"'
    
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 40
    
    # HEADER
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, y, "KADI SARVA VISHWAVIDYALAYA")
    y -= 18
    p.drawCentredString(width / 2, y, "LDRP Institute of Technology and Research")
    
    # TITLE
    y -= 25
    box_height = 25
    p.setLineWidth(2)
    p.rect(40, y - box_height, width - 80, box_height)
    p.line(40 + (width - 80) / 3, y - box_height, 40 + (width - 80) / 3, y)
    p.line(40 + 2 * (width - 80) / 3, y - box_height, 40 + 2 * (width - 80) / 3, y)
    
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, y - 16, f"Semester:{semester}")
    p.drawCentredString(width / 2, y - 16, "Seating Arrangement")
    p.drawRightString(width - 50, y - 16, f"{month} {year}")
    
    y -= box_height + 5
    
    # DATE
    p.setFont("Helvetica-Bold", 11)
    p.setLineWidth(1.5)
    p.rect(40, y - 20, width - 80, 20)
    p.drawCentredString(width / 2, y - 13, f"Date: {date_from} to {date_to}")
    
    y -= 30
    
    # TABLE
    seating_data = CESeating.objects.all()
    table_data = [
        ['Branch', 'Block No', 'Room No', 'Seat Nos', '', 'No. of Students'],
        ['', '', '', 'From', 'To', '']
    ]
    
    for i, r in enumerate(seating_data, start=1):
        table_data.append(['', str(i), str(r.room_no), str(r.seat_from), str(r.seat_to), str(r.count)])
    
    if table_data[2:]:
        table_data[2][0] = 'CE'
    
    t = Table(table_data, colWidths=[1.2*inch, 0.8*inch, 0.9*inch, 1*inch, 1*inch, 1.1*inch])
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 1), 'Helvetica-Bold', 11),
        ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONT', (0, 2), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (0, 2), (-1, -1), 'CENTER'),
    ]))
    
    table_width = 7.5 * inch
    t.wrapOn(p, table_width, height)
    t.drawOn(p, (width - table_width) / 2, y - (len(table_data) * 20))
    
    y = y - (len(table_data) * 20) - 20
    
    if note:
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, f"* {note}")
    
    # FOOTER
    p.setFont("Helvetica", 9)
    p.drawCentredString(width / 2, 30, "Prepared by Exam Section")
    
    p.save()
    return response
