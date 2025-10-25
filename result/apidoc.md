📚 Grade Management Endpoints
1. First Module Grades
GET /grade-1st-modules/
Description: Get list of first module grades
Permissions: Lecturers (all grades), Students (own grades only)

Query Parameters:

lecturer - Filter by lecturer ID

student - Filter by student ID

course - Filter by course ID

grade - Filter by grade (A+, A, B+, etc.)

search - Search in student names or course titles

ordering - Order by: student, course, total

Response:

json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "student": 123,
      "student_name": "John Doe",
      "student_id": "ST001",
      "course": 1,
      "course_title": "Mathematics",
      "course_code": "MATH101",
      "lecturer": 456,
      "lecturer_name": "Dr. Smith",
      "attendance": 10.00,
      "activities": 25.00,
      "exam": 45.00,
      "total": 80.00,
      "grade": "A-"
    }
  ]
}
POST /grade-1st-modules/
Description: Create new first module grade (Lecturers only)
Permissions: Lecturers

Request Body:

json
{
  "student": 123,
  "course": 1,
  "attendance": 10.00,
  "activities": 25.00,
  "exam": 45.00
}
GET /grade-1st-modules/{id}/
Description: Get specific first module grade
Permissions: Lecturers (any), Students (own only)

PUT/PATCH /grade-1st-modules/{id}/
Description: Update first module grade (Lecturers only)
Permissions: Lecturers

DELETE /grade-1st-modules/{id}/
Description: Delete first module grade (Lecturers only)
Permissions: Lecturers

GET /grade-1st-modules/course/{course_id}/
Description: Get grades for specific course
Permissions: Lecturers (all), Students (own only)

2. Second Module Grades
GET /grade-2nd-modules/
Description: Get list of second module grades
Permissions: Lecturers (all grades), Students (own grades only)

Query Parameters: Same as first module

POST /grade-2nd-modules/
Description: Create new second module grade (Lecturers only)
Permissions: Lecturers

GET /grade-2nd-modules/{id}/
Description: Get specific second module grade
Permissions: Lecturers (any), Students (own only)

PUT/PATCH /grade-2nd-modules/{id}/
Description: Update second module grade (Lecturers only)
Permissions: Lecturers

DELETE /grade-2nd-modules/{id}/
Description: Delete second module grade (Lecturers only)
Permissions: Lecturers

GET /grade-2nd-modules/course/{course_id}/
Description: Get grades for specific course
Permissions: Lecturers (all), Students (own only)

3. Semester Grades
GET /grade-semesters/
Description: Get list of semester grades
Permissions: Lecturers (all grades), Students (own grades only)

Query Parameters:

All previous parameters plus:

semester - Filter by semester ID

POST /grade-semesters/
Description: Create new semester grade (Lecturers only)
Permissions: Lecturers

GET /grade-semesters/{id}/
Description: Get specific semester grade
Permissions: Lecturers (any), Students (own only)

PUT/PATCH /grade-semesters/{id}/
Description: Update semester grade (Lecturers only)
Permissions: Lecturers

DELETE /grade-semesters/{id}/
Description: Delete semester grade (Lecturers only)
Permissions: Lecturers

GET /grade-semesters/course/{course_id}/
Description: Get grades for specific course
Permissions: Lecturers (all), Students (own only)

GET /grade-semesters/my_grades/
Description: Get current student's semester grades
Permissions: Students only

Response:

json
[
  {
    "id": 1,
    "student": 123,
    "student_name": "John Doe",
    "student_id": "ST001",
    "course": 1,
    "course_title": "Mathematics",
    "course_code": "MATH101",
    "lecturer": 456,
    "lecturer_name": "Dr. Smith",
    "semester": 1,
    "semester_name": "Fall 2024",
    "attendance": 10.00,
    "activities": 25.00,
    "exam": 45.00,
    "total": 80.00,
    "grade": "A-"
  }
]
GET /grade-semesters/my_all_grades/
Description: Get all grades for current student (all modules)
Permissions: Students only

Response:

json
{
  "first_module_grades": [
    {
      "id": 1,
      "student": 123,
      "student_name": "John Doe",
      "student_id": "ST001",
      "course": 1,
      "course_title": "Mathematics",
      "course_code": "MATH101",
      "lecturer": 456,
      "lecturer_name": "Dr. Smith",
      "attendance": 10.00,
      "activities": 25.00,
      "exam": 45.00,
      "total": 80.00,
      "grade": "A-"
    }
  ],
  "second_module_grades": [
    {
      "id": 2,
      "student": 123,
      "student_name": "John Doe",
      "student_id": "ST001",
      "course": 1,
      "course_title": "Mathematics",
      "course_code": "MATH101",
      "lecturer": 456,
      "lecturer_name": "Dr. Smith",
      "attendance": 8.00,
      "activities": 28.00,
      "exam": 48.00,
      "total": 84.00,
      "grade": "A"
    }
  ],
  "semester_grades": [
    {
      "id": 3,
      "student": 123,
      "student_name": "John Doe",
      "student_id": "ST001",
      "course": 1,
      "course_title": "Mathematics",
      "course_code": "MATH101",
      "lecturer": 456,
      "lecturer_name": "Dr. Smith",
      "semester": 1,
      "semester_name": "Fall 2024",
      "attendance": 18.00,
      "activities": 53.00,
      "exam": 93.00,
      "total": 164.00,
      "grade": "A"
    }
  ]
}
4. Lecturer Operations
POST /lecturer-grades/bulk_update_grades/
Description: Bulk update grades for multiple students
Permissions: Lecturers only

Request Body:

json
{
  "course_id": 1,
  "grade_type": "1st_module",
  "grades": [
    {
      "student_id": 123,
      "attendance": 10.00,
      "activities": 25.00,
      "exam": 45.00
    },
    {
      "student_id": 124,
      "attendance": 8.00,
      "activities": 22.00,
      "exam": 50.00
    }
  ]
}
Parameters:

course_id (integer, required): Course ID

grade_type (string, required): "1st_module", "2nd_module", or "semester"

grades (array, required): List of grade objects

student_id (integer, required): Student ID

attendance (decimal, optional): Attendance score

activities (decimal, optional): Activities score

exam (decimal, optional): Exam score

Response:

json
{
  "detail": "Successfully updated 2 grades",
  "updated_grades": [
    {
      "student_id": 123,
      "student_name": "John Doe",
      "attendance": 10.00,
      "activities": 25.00,
      "exam": 45.00,
      "total": 80.00
    }
  ]
}
GET /lecturer-grades/course_students_grades/
Description: Get all students and their grades for specific course
Permissions: Lecturers only

Query Parameters:

course_id (required): Course ID

Response:

json
{
  "first_module": [
    {
      "id": 1,
      "student": 123,
      "student_name": "John Doe",
      "student_id": "ST001",
      "course": 1,
      "course_title": "Mathematics",
      "course_code": "MATH101",
      "lecturer": 456,
      "lecturer_name": "Dr. Smith",
      "attendance": 10.00,
      "activities": 25.00,
      "exam": 45.00,
      "total": 80.00,
      "grade": "A-"
    }
  ],
  "second_module": [],
  "semester": []
}
🔐 Permission Matrix
Lecturers
Endpoint	GET	POST	PUT/PATCH	DELETE
/grade-1st-modules/	✅ All	✅	✅	✅
/grade-2nd-modules/	✅ All	✅	✅	✅
/grade-semesters/	✅ All	✅	✅	✅
/lecturer-grades/bulk_update_grades/	❌	✅	❌	❌
/lecturer-grades/course_students_grades/	✅	❌	❌	❌
Students
Endpoint	GET	POST	PUT/PATCH	DELETE
/grade-1st-modules/	✅ Own only	❌	❌	❌
/grade-2nd-modules/	✅ Own only	❌	❌	❌
/grade-semesters/	✅ Own only	❌	❌	❌
/grade-semesters/my_grades/	✅	❌	❌	❌
/grade-semesters/my_all_grades/	✅	❌	❌	❌
/lecturer-grades/*	❌	❌	❌	❌
📊 Grade Calculation
Total Score Calculation
text
total = attendance + activities + exam
Grade Mapping
Total Score	Grade
≥ 90%	A+
≥ 85%	A
≥ 80%	A-
≥ 75%	B+
≥ 70%	B
≥ 65%	B-
≥ 60%	C+
≥ 55%	C
≥ 50%	C-
≥ 45%	D
< 45%	F
🔍 Filtering and Search
Available Filters
By lecturer: ?lecturer=1

By student: ?student=123

By course: ?course=1

By grade: ?grade=A+

By semester: ?semester=1 (semester grades only)

Search Fields
Student first name

Student last name

Course title

Course code

Ordering Options
Student name

Course title

Total score

Semester (semester grades only)

❌ Error Responses
Common HTTP Status Codes
400 Bad Request - Invalid input data

401 Unauthorized - Authentication required

403 Forbidden - Insufficient permissions

404 Not Found - Resource not found

500 Internal Server Error - Server error

Example Error Response
json
{
  "detail": "Only lecturers can update grades",
  "code": "permission_denied"
}
📝 Notes
Grade Auto-calculation: Total score and grade are automatically calculated when saving

Unique Constraints: Each student can have only one grade record per course/module combination

Bulk Operations: Use bulk update for efficient grade management of multiple students

Read-Only for Students: Students can only view their own grades, not modify them

Real-time Updates: Grade changes are immediately reflected in the system