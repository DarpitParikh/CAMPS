# Academic & Examination Management System

## Overview
A faculty-oriented Academic & Examination Management System built for LDRP Institute of Technology and Research. Designed to replace Excel-based workflows with a simple, smart, time-saving internal portal.

**Project Type:** 8th Semester CSE Project
**Built With:** Python Django + HTML + SQLite

---

## 📋 Core Features Implemented

### 1. **Faculty-Only Login (Role-Based)**
- Admin (Exam Cell) & Faculty roles
- Session-based authentication
- Faculty can only edit their own subjects
- Admin controls all structure and exam operations

### 2. **Semester-Wise Student Management**
- Store students with roll number, name, branch, semester
- Global search by roll number, name, or enrollment number
- Filter by branch and semester
- Add new students (Admin only)

### 3. **Student Profile Page** ⭐ Key Differentiator
One complete page showing:
- Basic student details (roll number, enrollment, branch, semester)
- Attendance summary (subject-wise percentage)
- Marks summary (internal + external, total, grade, pass/fail)
- Exam seating info (exam number, room, seat)

### 4. **Daily Attendance** ✅ Faster Than Excel
- Faculty selects subject + date
- Student list loads automatically
- Default: Present (faculty clicks only to mark absent)
- One-click save with auto percentage calculation
- Context memory: remembers last subject used

### 5. **Marks Management**
- Subject-wise marks entry
- Internal + External marks input
- Auto total calculation
- Grade assignment (A+, A, B+, B, C, F)
- Pass/fail logic (>=40 passes)
- Max marks validation
- Safe-edit: Lock after final submit

### 6. **Automated Exam Seating + Direct Print**
- Input: total students, students per room
- Auto room allocation algorithm
- Handles leftover students intelligently
- Print-ready PDF output
- Shows current allocation status

### 7. **Smart Dashboard**
- **Admin Dashboard:** Overview of students, subjects, faculty, recent activities
- **Faculty Dashboard:** Quick access to subjects, pending work indicators
- Context memory: Shows last accessed subject

---

## 🏗️ Project Structure

```
examhall/
├── allocation/
│   ├── models.py              # All database models
│   ├── views.py               # All view logic
│   ├── forms.py               # All forms
│   ├── urls.py                # URL routing
│   ├── auth_views.py          # Login/Logout views
│   ├── admin.py               # Admin configuration
│   ├── templates/
│   │   ├── auth/
│   │   │   └── login.html
│   │   ├── dashboard/
│   │   │   ├── admin_dashboard.html
│   │   │   └── faculty_dashboard.html
│   │   ├── students/
│   │   │   ├── student_list.html
│   │   │   ├── student_profile.html
│   │   │   └── add_student.html
│   │   ├── attendance/
│   │   │   └── mark_attendance.html
│   │   ├── marks/
│   │   │   └── marks_entry.html
│   │   ├── allocate.html
│   │   └── preview.html
│   ├── migrations/
│   └── __pycache__/
├── examhall/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── db.sqlite3
└── README.md
```

---

## 💾 Database Models

### Academic Structure
- **Branch** - Engineering branches (CE, ME, EC, EE, CS)
- **Semester** - Semester numbers (1-8)
- **Subject** - Subject code, name, max marks (internal + external)

### People
- **Faculty** - Teacher info, subjects taught, last accessed subject/semester
- **Student** - Roll number, name, branch, semester, exam seating info

### Academic Records
- **StudentSubject** - Student-Subject enrollment
- **Attendance** - Daily attendance records (Present/Absent)
- **Marks** - Subject-wise marks (internal, external, total, grade)

### Exam Seating
- **CESeating** - Room allocation data

---

## 🔐 Access Control

### Admin (Exam Cell)
- ✓ View all students
- ✓ Add/edit students
- ✓ Manage exam seating
- ✓ Download PDF reports
- ✓ View all attendance/marks

### Faculty
- ✓ View only assigned students
- ✓ Mark attendance for their subjects
- ✓ Enter marks for their subjects
- ✓ Submit & lock marks (prevent accidental changes)

---

## 🚀 Setup Instructions

### Prerequisites
```bash
Python 3.9+
pip
Virtual Environment (recommended)
```

### Installation Steps

1. **Clone/Extract Project**
   ```bash
   cd examhall
   ```

2. **Create Virtual Environment** (Optional but Recommended)
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install django pandas openpyxl reportlab
   ```

4. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create Superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```
   Follow prompts to create admin account

6. **Create Sample Data** (Optional)
   ```bash
   python manage.py shell
   
   # Create branches
   from allocation.models import Branch, Semester
   Branch.objects.create(name='Civil Engineering', code='CE')
   Branch.objects.create(name='Mechanical Engineering', code='ME')
   Branch.objects.create(name='Computer Science', code='CS')
   
   # Create semesters
   for i in range(1, 9):
       Semester.objects.create(number=i)
   
   exit()
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access Application**
   - URL: `http://127.0.0.1:8000/`
   - Admin: `http://127.0.0.1:8000/admin/`
   - Use created superuser credentials to login

---

## 👤 Creating User Accounts

### Via Django Admin
1. Login to `/admin/`
2. Create User
3. Create Faculty record if needed
4. Assign subjects

### Via Shell
```bash
python manage.py shell

from django.contrib.auth.models import User
from allocation.models import Faculty, Subject

# Create faculty user
user = User.objects.create_user(
    username='faculty1',
    password='password123',
    first_name='Prof',
    last_name='Name'
)

# Create faculty profile
faculty = Faculty.objects.create(
    user=user,
    employee_id='EMP001'
)

# Assign subjects
faculty.subjects.add(subject_id)  # Add subject IDs
faculty.save()

exit()
```

---

## 📖 Usage Guide

### 1. **Faculty Workflow**

#### Mark Attendance
1. Login to dashboard
2. Click "Mark Attendance"
3. Select subject
4. Select date
5. Click "Load Students"
6. Default is Present - Click to mark Absent
7. Click "Save Attendance"

#### Enter Marks
1. Click "Enter Marks"
2. Select subject
3. Auto-loads all enrolled students
4. Enter internal marks (max = subject's internal max)
5. Enter external marks (max = subject's external max)
6. Total calculates automatically
7. Click "Save Marks" to save (can edit later)
8. Click "Submit & Lock" when final

### 2. **Admin Workflow**

#### Manage Students
1. Click "Manage Students"
2. Search by name/roll number
3. Filter by branch/semester
4. Click "View Profile" for details
5. Click "Add New Student" to add

#### Exam Seating
1. Click "Exam Seating"
2. Fill form:
   - Semester, Month, Year
   - Date range
   - Total students
   - Students per room
   - Rooms (e.g., 301-305, 401-403)
3. Click "Generate Seating"
4. Preview shows room allocation
5. Click "Download PDF" for print-ready file

### 3. **View Reports**

#### Student Profile
- Shows complete academic record
- Attendance % for each subject
- Marks, grades, pass/fail status
- Exam seating details

#### Dashboard
- Admin sees: Total students, subjects, faculty, recent activities
- Faculty sees: Assigned subjects, pending work

---

## 🎨 UI Design Philosophy

- **Minimal:** Clean, focused interface
- **Workflow-Driven:** Designed around actual faculty tasks
- **Student-Centric:** Views organized around student data
- **Error Prevention:** Validation, constraints, lock mechanisms
- **Context Memory:** Remembers last accessed subject/semester

---

## 📱 Browser Support
- Chrome (Recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (Basic support)

---

## 🔒 Security Notes

- Passwords stored using Django's default hashing
- CSRF protection enabled
- SQL injection prevention (ORM)
- Session-based authentication
- Admin-only operations protected

---

## 📊 Limitations & Scope

❌ **NOT Implemented**
- Student login/self-service
- Mobile app
- Charts/analytics
- AI/ML features
- Email notifications
- Real-time updates

✅ **By Design**
- No over-engineering
- Code is readable and viva-friendly
- Minimal dependencies
- Fast performance
- Easy to modify

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001  # Use different port
```

### Database Errors
```bash
python manage.py makemigrations
python manage.py migrate
```

### Import Errors
```bash
pip install --upgrade django pandas openpyxl reportlab
```

### Login Not Working
- Check if user exists in admin panel
- Check if correct username/password
- Clear browser cookies and try again

---

## 📝 Development Notes

### Adding New Features
1. Update models.py
2. Create migration: `python manage.py makemigrations`
3. Apply migration: `python manage.py migrate`
4. Add view in views.py
5. Add URL in urls.py
6. Create template in templates/

### Customization Points
- Semester count in Semester model (currently 1-8)
- Max marks validation in Marks model
- Grade boundaries in Marks.get_grade()
- Attendance percentage threshold
- Room allocation algorithm in views.py

---

## 📄 License
Educational Project - LDRP Institute of Technology and Research

---

## 👨‍💼 Viva Preparation

### Key Concepts to Explain
1. **Role-Based Access Control** - Middleware, decorators
2. **Database Design** - Relationships, constraints
3. **Attendance Algorithm** - Default present logic
4. **Marks Calculation** - Grade logic, pass/fail
5. **Exam Seating** - Room allocation algorithm
6. **State Management** - Context memory in Faculty model
7. **PDF Generation** - ReportLab usage

### Code to Show
- Authentication views
- Dashboard logic
- Marks calculation
- Attendance marking
- Room allocation algorithm

---

## 📞 Support

For issues or clarifications, check:
1. Error messages in Django console
2. Browser console (F12)
3. Admin panel for data verification
4. Database queries using `python manage.py dbshell`

---

**Built with ❤️ for LDRP Institute**

Last Updated: December 2025
