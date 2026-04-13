from decimal import Decimal

from course.models import Course, CourseAllocation, Program
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import Student
from core.models import Semester
from result.models import Grade_1st_module, Grade_2nd_module, Grade_semester

User = get_user_model()


class ResultViewsTestCase(APITestCase):
    """Тесты для views результатов"""

    def setUp(self):
        """Настройка тестовых данных"""
        # Создаем семестр
        self.semester = Semester.objects.create(
            semester="First", is_current_semester=True
        )

        # Создаем программу
        self.program = Program.objects.create(
            title="Computer Science", summary="CS Program"
        )

        # Создаем преподавателя
        self.lecturer = User.objects.create_user(
            username="lecturer1",
            email="lecturer@test.com",
            password="testpass123",
            is_lecturer=True,
            first_name="John",
            last_name="Doe",
        )

        # Создаем студента
        self.student_user = User.objects.create_user(
            username="student1",
            email="student@test.com",
            password="testpass123",
            is_student=True,
            first_name="Jane",
            last_name="Smith",
        )

        self.student = Student.objects.create(
            student=self.student_user, level="100", program=self.program
        )

        # Создаем второго студента
        self.student_user2 = User.objects.create_user(
            username="student2",
            email="student2@test.com",
            password="testpass123",
            is_student=True,
            first_name="Bob",
            last_name="Johnson",
        )

        self.student2 = Student.objects.create(
            student=self.student_user2, level="100", program=self.program
        )

        # Создаем курс
        self.course = Course.objects.create(
            title="Introduction to Programming",
            code="CS101",
            credit=3,
            level="100",
            semester="First",
            year=1,
        )

        # Создаем allocation для преподавателя
        self.allocation = CourseAllocation.objects.create(
            lecturer=self.lecturer, semester=self.semester
        )
        self.allocation.courses.add(self.course)

        # Создаем оценки для первого модуля
        self.grade_1st = Grade_1st_module.objects.create(
            lecturer=self.lecturer,
            student=self.student,
            course=self.course,
            attendance=Decimal("20.00"),
            activities=Decimal("25.00"),
            exam=Decimal("30.00"),
            total=Decimal("75.00"),
            grade="B+",
        )

        self.grade_1st_2 = Grade_1st_module.objects.create(
            lecturer=self.lecturer,
            student=self.student2,
            course=self.course,
            attendance=Decimal("15.00"),
            activities=Decimal("20.00"),
            exam=Decimal("25.00"),
            total=Decimal("60.00"),
            grade="C+",
        )

        # Создаем оценки для второго модуля
        self.grade_2nd = Grade_2nd_module.objects.create(
            lecturer=self.lecturer,
            student=self.student,
            course=self.course,
            attendance=Decimal("22.00"),
            activities=Decimal("28.00"),
            exam=Decimal("35.00"),
            total=Decimal("85.00"),
            grade="A",
        )

        # Создаем семестровые оценки
        self.grade_semester = Grade_semester.objects.create(
            lecturer=self.lecturer,
            student=self.student,
            course=self.course,
            semester=self.semester,
            attendance=Decimal("21.00"),
            activities=Decimal("26.00"),
            exam=Decimal("33.00"),
            total=Decimal("80.00"),
            grade="A-",
        )

        self.client = APIClient()

    def test_bulk_update_as_lecturer_success(self):
        """Тест: Преподаватель может массово обновить оценки"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("lecturer-bulk-grades-bulk-update")
        data = {
            "course_id": self.course.id,
            "grade_type": "1st_module",
            "grades": [
                {
                    "student_id": self.student.id,
                    "attendance": 25.00,
                    "activities": 30.00,
                    "exam": 35.00,
                },
                {
                    "student_id": self.student2.id,
                    "attendance": 20.00,
                    "activities": 25.00,
                    "exam": 30.00,
                },
            ],
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.assertIn("Successfully updated", response.data["detail"])
        self.assertEqual(len(response.data["updated_grades"]), 2)

        # Проверяем, что оценки обновились
        self.grade_1st.refresh_from_db()
        self.assertEqual(float(self.grade_1st.attendance), 25.00)
        self.assertEqual(float(self.grade_1st.activities), 30.00)
        self.assertEqual(float(self.grade_1st.exam), 35.00)
        self.assertEqual(float(self.grade_1st.total), 90.00)

    def test_bulk_update_without_authentication(self):
        """Тест: Неавторизованный пользователь не может обновить оценки"""
        url = reverse("lecturer-bulk-grades-bulk-update")
        data = {"course_id": self.course.id, "grade_type": "1st_module", "grades": []}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bulk_update_as_student_forbidden(self):
        """Тест: Студент не может массово обновить оценки"""
        self.client.force_authenticate(user=self.student_user)

        url = reverse("lecturer-bulk-grades-bulk-update")
        data = {
            "course_id": self.course.id,
            "grade_type": "1st_module",
            "grades": [{"student_id": self.student.id, "attendance": 25.00}],
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Only lecturers", response.data["detail"])

    def test_bulk_update_missing_required_fields(self):
        """Тест: Ошибка при отсутствии обязательных полей"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("lecturer-bulk-grades-bulk-update")
        data = {
            "course_id": self.course.id,
            # Отсутствует grade_type
            "grades": [],
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("grade_type", response.data)

    def test_bulk_update_invalid_grade_type(self):
        """Тест: Ошибка при неверном типе оценки"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("lecturer-bulk-grades-bulk-update")
        data = {"course_id": self.course.id, "grade_type": "invalid_type", "grades": []}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_update_nonexistent_grade(self):
        """Тест: Ошибка при попытке обновить несуществующую оценку"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("lecturer-bulk-grades-bulk-update")
        data = {
            "course_id": self.course.id,
            "grade_type": "1st_module",
            "grades": [
                {"student_id": 99999, "attendance": 25.00}  # Несуществующий студент
            ],
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("not found", response.data["detail"])

    def test_bulk_update_2nd_module(self):
        """Тест: Массовое обновление оценок второго модуля"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("lecturer-bulk-grades-bulk-update")
        data = {
            "course_id": self.course.id,
            "grade_type": "2nd_module",
            "grades": [
                {
                    "student_id": self.student.id,
                    "attendance": 24.00,
                    "activities": 29.00,
                    "exam": 37.00,
                }
            ],
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем обновление
        self.grade_2nd.refresh_from_db()
        self.assertEqual(float(self.grade_2nd.attendance), 24.00)
        self.assertEqual(float(self.grade_2nd.activities), 29.00)
        self.assertEqual(float(self.grade_2nd.exam), 37.00)
        self.assertEqual(float(self.grade_2nd.total), 90.00)

    def test_bulk_update_semester(self):
        """Тест: Массовое обновление семестровых оценок"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("lecturer-bulk-grades-bulk-update")
        data = {
            "course_id": self.course.id,
            "grade_type": "semester",
            "grades": [
                {
                    "student_id": self.student.id,
                    "attendance": 23.00,
                    "activities": 27.00,
                    "exam": 40.00,
                }
            ],
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем обновление
        self.grade_semester.refresh_from_db()
        self.assertEqual(float(self.grade_semester.attendance), 23.00)
        self.assertEqual(float(self.grade_semester.activities), 27.00)
        self.assertEqual(float(self.grade_semester.exam), 40.00)
        self.assertEqual(float(self.grade_semester.total), 90.00)

    def test_bulk_update_partial_fields(self):
        """Тест: Обновление только некоторых полей оценки"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("lecturer-bulk-grades-bulk-update")
        initial_activities = float(self.grade_1st.activities)
        initial_exam = float(self.grade_1st.exam)

        data = {
            "course_id": self.course.id,
            "grade_type": "1st_module",
            "grades": [
                {
                    "student_id": self.student.id,
                    "attendance": 28.00,  # Обновляем только attendance
                }
            ],
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что attendance обновился, а остальные поля не изменились
        self.grade_1st.refresh_from_db()
        self.assertEqual(float(self.grade_1st.attendance), 28.00)
        self.assertEqual(float(self.grade_1st.activities), initial_activities)
        self.assertEqual(float(self.grade_1st.exam), initial_exam)

    def test_grade_1st_module_list_as_lecturer(self):
        """Тест: Преподаватель может получить список оценок первого модуля"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("grade-1st-modules-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_grade_1st_module_list_as_student(self):
        """Тест: Студент может видеть только свои оценки"""
        self.client.force_authenticate(user=self.student_user)

        url = reverse("grade-1st-modules-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["student"], self.student.id)

    def test_grade_by_course(self):
        """Тест: Получение оценок по конкретному курсу"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse(
            "grade-1st-modules-by-course", kwargs={"course_id": self.course.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_my_grades_as_student(self):
        """Тест: Студент получает свои семестровые оценки"""
        self.client.force_authenticate(user=self.student_user)

        url = reverse("grade-semesters-my-grades")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_my_grades_as_lecturer_forbidden(self):
        """Тест: Преподаватель не может использовать my_grades endpoint"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("grade-semesters-my-grades")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_my_all_grades_as_student(self):
        """Тест: Студент получает все свои оценки (все модули)"""
        self.client.force_authenticate(user=self.student_user)

        url = reverse("grade-semesters-my-all-grades")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("first_module_grades", response.data)
        self.assertIn("second_module_grades", response.data)
        self.assertIn("semester_grades", response.data)

    def test_lecturer_course_grades(self):
        """Тест: Преподаватель получает оценки студентов по курсу"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("lecturer-course-grades-course-grades")
        response = self.client.get(url, {"course_id": self.course.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("first_module", response.data)
        self.assertIn("second_module", response.data)
        self.assertIn("semester", response.data)

    def test_lecturer_course_grades_without_course_id(self):
        """Тест: Ошибка при отсутствии course_id параметра"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("lecturer-course-grades-course-grades")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("course_id parameter is required", response.data["detail"])

    def test_lecturer_course_grades_as_student_forbidden(self):
        """Тест: Студент не может использовать lecturer course grades endpoint"""
        self.client.force_authenticate(user=self.student_user)

        url = reverse("lecturer-course-grades-course-grades")
        response = self.client.get(url, {"course_id": self.course.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grade_filtering(self):
        """Тест: Фильтрация оценок"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("grade-1st-modules-list")
        response = self.client.get(url, {"student": self.student.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["student"], self.student.id)

    def test_grade_searching(self):
        """Тест: Поиск по оценкам"""
        self.client.force_authenticate(user=self.lecturer)

        url = reverse("grade-1st-modules-list")
        response = self.client.get(url, {"search": "Jane"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)
