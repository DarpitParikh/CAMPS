# Student List Feature - README

## New Feature: Upload Student List and Auto-assign Exam Numbers

### What's New:
✅ Upload Excel (.xlsx) or CSV files with student information
✅ Automatically assign exam numbers starting from your chosen number
✅ Students are distributed across rooms based on seating allocation
✅ View and download student list with exam numbers, enrollment numbers, names, and room assignments

### How to Use:

1. **Prepare Your Student File:**
   - Create an Excel (.xlsx) or CSV (.csv) file
   - Must have 2 columns:
     - Column 1: Enrollment Number
     - Column 2: Student Name
   - See `sample_students.csv` for reference

2. **Fill the Form:**
   - Enter semester, month, year, and date range
   - **Starting Exam No**: Enter the first exam number (e.g., 227001)
   - **Upload Student List**: Choose your Excel/CSV file
   - Enter starting seat number and total students
   - Set preferred and max students per room
   - Enter room numbers (e.g., 301-305,307)
   - Optional: Add a note

3. **Generate:**
   - Click "Generate Seating Arrangement"
   - View the seating allocation
   - Click "View Student List" to see all students with their assigned exam numbers and rooms

4. **Download:**
   - Download Seating Arrangement PDF (rooms and seat numbers)
   - Download Student List PDF (exam numbers, enrollment numbers, names, rooms)

### File Format Examples:

**CSV Format (sample_students.csv):**
```
Enrollment No,Student Name
21BECE30079,GAMIT ANGELKUMARI HITESHBHAI
21BECE30099,JADODIYA KASHYAP JAYESHBHAI
```

**Excel Format:**
Same structure - just save as .xlsx file

### Features:
- Students are automatically assigned to rooms in order
- Exam numbers increment sequentially
- Each student gets their room assignment
- Professional PDF output matching your image format
- Print-friendly student list

### Notes:
- File must have at least 2 columns
- Column headers don't matter (can be anything)
- Only first 2 columns are used (Enrollment No, Student Name)
- Students are limited to the "Total Students" count you enter
- Students are distributed according to room allocation logic
