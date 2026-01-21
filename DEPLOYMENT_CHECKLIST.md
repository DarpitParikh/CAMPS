# 🚀 Academic Management System - Setup & Deployment Checklist

## ✅ Pre-Deployment Checklist

### Database Setup
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Verify database created: `db.sqlite3` exists
- [ ] Check Django admin accessible: `/admin/`

### Initial Data Setup
- [ ] Create at least 1 Branch via admin
- [ ] Create Semesters 1-8 via admin or shell
- [ ] Create at least 1 Subject (assign to branch + semester)
- [ ] Create Faculty user and assign subjects
- [ ] Create at least 1 Student

### Code Verification
- [ ] All models imported in admin.py
- [ ] All URLs configured in allocation/urls.py
- [ ] All templates present in templates/ directory
- [ ] No import errors: `python manage.py check`

### Performance Check
- [ ] Database queries optimized
- [ ] Static files working
- [ ] Templates rendering correctly

---

## 📦 Installation Quick Reference

### Windows
```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install django pandas openpyxl reportlab

# 3. Setup database
python manage.py migrate

# 4. Create admin user
python manage.py createsuperuser

# 5. Run server
python manage.py runserver
```

### Mac/Linux
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install django pandas openpyxl reportlab

# 3. Setup database
python manage.py migrate

# 4. Create admin user
python manage.py createsuperuser

# 5. Run server
python manage.py runserver
```

---

## 🔑 Key URLs

| Page | URL | Access |
|------|-----|--------|
| Login | `/login/` | Public |
| Dashboard | `/` | Authenticated |
| Admin Dashboard | `/` | Admin Only |
| Faculty Dashboard | `/` | Faculty Only |
| Student List | `/students/` | Faculty + Admin |
| Student Profile | `/student/<id>/` | Faculty + Admin |
| Add Student | `/students/add/` | Admin Only |
| Mark Attendance | `/attendance/` | Faculty |
| Marks Entry | `/marks/` | Faculty |
| Submit Marks | `/marks/submit/<id>/` | Faculty |
| Exam Seating | `/allocate/` | Admin Only |
| Seating Preview | `/preview/` | Admin Only |
| Download Seating PDF | `/download/` | Admin Only |
| Django Admin | `/admin/` | Superuser Only |

---

## 👥 Test User Setup

### Create Test Admin
```bash
python manage.py createsuperuser
# Username: admin
# Password: admin123
```

### Create Test Faculty (via admin)
1. Create User: `Dr. Smith`, username `smith`, password `smith123`
2. Make staff: Yes
3. Create Faculty record, assign subjects
4. Logout, login as faculty to test

### Create Test Student (via admin or add form)
1. Roll Number: `CE001`
2. Enrollment: `ENG001`
3. Name: `John Doe`
4. Branch: `Civil Engineering`
5. Semester: `1`

---

## 🧪 Testing Workflow

### Test Attendance Marking
1. Login as faculty
2. Click "Mark Attendance"
3. Select subject + date
4. Mark some students absent
5. Save and verify

### Test Marks Entry
1. Click "Enter Marks"
2. Select subject
3. Enter marks for students
4. Save
5. Click "Submit & Lock"

### Test Student Profile
1. Go to Student List
2. Click "View Profile" on student
3. Verify all sections display correctly

### Test Exam Seating
1. Login as admin
2. Click "Exam Seating" (or `/allocate/`)
3. Fill form:
   - Total students: 50
   - Students per room: 31
   - Max per room: 36
   - Rooms: 301-303
4. Generate and preview
5. Download PDF

---

## 🐛 Common Issues & Solutions

### Issue: "No module named 'django'"
**Solution:**
```bash
pip install django pandas openpyxl reportlab
```

### Issue: "OperationalError: no such table"
**Solution:**
```bash
python manage.py migrate
```

### Issue: "Port 8000 already in use"
**Solution:**
```bash
python manage.py runserver 8001
```

### Issue: Admin panel not loading
**Solution:**
```bash
python manage.py collectstatic --noinput
```

### Issue: Login page blank/not loading
**Solution:**
1. Check templates directory structure
2. Verify `allocation/templates/auth/login.html` exists
3. Restart server

---

## 📊 Database Models Quick Reference

### Models with Admin Interface
- ✅ Branch
- ✅ Semester
- ✅ Subject
- ✅ Faculty
- ✅ Student
- ✅ StudentSubject
- ✅ Attendance
- ✅ Marks
- ✅ CESeating

### Key Relationships
```
Faculty 1---* Subject
Student 1---* StudentSubject ---* Subject
Student 1---* Attendance
Student 1---* Marks
```

---

## 🔒 Security Reminders

- [ ] Change SECRET_KEY in settings.py for production
- [ ] Set DEBUG = False for production
- [ ] Use HTTPS in production
- [ ] Configure ALLOWED_HOSTS
- [ ] Use environment variables for sensitive data
- [ ] Regular database backups
- [ ] Keep Django updated: `pip install --upgrade django`

---

## 📝 Customization Guide

### Change Institution Name
- File: All templates
- Change: "LDRP Institute" to your institution

### Modify Semester Count
- File: `models.py`
- Change: `Semester.objects.create(number=i)` range (1-8)

### Adjust Max Marks
- File: `models.py` > Subject model
- Change: `max_marks = models.IntegerField(default=100)`

### Change Grade Boundaries
- File: `models.py` > Marks.get_grade()
- Modify: Grade conditions (>=90, >=80, etc.)

---

## 📞 Troubleshooting Contacts

### For Django/Python Issues
- Documentation: https://docs.djangoproject.com/
- Stack Overflow: Tag `django`

### For Database Issues
- SQLite documentation

### For UI/Template Issues
- Check browser console (F12)
- Django error page (when DEBUG=True)

---

## ✨ Features Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Faculty Login | ✅ Complete | Role-based |
| Student Management | ✅ Complete | CRUD operations |
| Student Profile | ✅ Complete | Shows attendance + marks |
| Attendance | ✅ Complete | Fast marking |
| Marks Entry | ✅ Complete | Auto calculation |
| Exam Seating | ✅ Complete | Auto allocation |
| Dashboard | ✅ Complete | Admin + Faculty views |
| PDF Export | ✅ Complete | Seating lists |
| Context Memory | ✅ Complete | Remembers last subject |
| Pending Indicators | ✅ Complete | Shows incomplete work |

---

## 🎓 For Viva Preparation

### Must Know Topics
1. Role-based access control implementation
2. Database design and relationships
3. Attendance algorithm (default present)
4. Marks calculation logic
5. Room allocation algorithm
6. Django ORM queries
7. Template rendering
8. Authentication system

### Code Locations
- Authentication: `auth_views.py`
- Dashboard Logic: `views.py` (dashboard functions)
- Attendance: `views.py` > `mark_attendance()`
- Marks: `views.py` > `marks_entry()`
- Room Allocation: `views.py` > `allocate()`

### Talking Points
- "Faculty-first design"
- "Prevents mistakes instead of correcting"
- "Context memory for productivity"
- "Smart allocation algorithm"
- "Role-based security"

---

## 📅 Post-Launch

### Monitor
- Check Django logs for errors
- Monitor database size
- Track user feedback

### Maintain
- Regular backups
- Update dependencies quarterly
- Add new features as needed

### Scale
- If many users, consider PostgreSQL
- Use gunicorn + nginx for production
- Add caching layer (Redis)

---

**Last Updated:** December 2025
**System Version:** 1.0
**Django Version:** 5.2
**Python Version:** 3.9+

---

🎉 **System Ready for Deployment!**
