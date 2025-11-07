from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from datetime import time

from accounts.models import Student, Group
from course.models import Course, Program
from attendance.models import ScheduleItem, Attendance

User = get_user_model()


class ScheduleItemModelTest(TestCase):
    """Тесты для модели ScheduleItem"""
    
    def setUp(self):
        self.program = Program.objects.create(
            title="Computer Science",
            summary="CS Program"
        )
        self.course = Course.objects.create(
            title="Python Programming",
            code="CS101",
            credit=3,
            program=self.program
        )
        self.group = Group.objects.create(name="Group A")
    
    def test_schedule_item_creation(self):
        """Тест создания занятия в расписании"""
        schedule = ScheduleItem.objects.create(
            course=self.course,
            group=self.group,
            order=1,
            day="Monday",
            start=time(9, 0),
            end=time(10, 30)
        )
        self.assertEqual(schedule.course, self.course)
        self.assertEqual(schedule.group, self.group)
        self.assertEqual(schedule.day, "Monday")


class AttendanceModelTest(TestCase):
    """Тесты для модели Attendance"""
    
    def setUp(self):
        # Создаем пользователя-студента
        self.user = User.objects.create_user(
            username="student1",
            password="password123",
            is_student=True
        )
        self.student = Student.objects.create(
            student=self.user,
            level="Bachelor"
        )
        
        # Создаем программу и курс
        self.program = Program.objects.create(
            title="Computer Science",
            summary="CS Program"
        )
        self.course = Course.objects.create(
            title="Python Programming",
            code="CS101",
            credit=3,
            program=self.program
        )
        self.group = Group.objects.create(name="Group A")
        
        # Создаем расписание
        self.schedule = ScheduleItem.objects.create(
            course=self.course,
            group=self.group,
            order=1,
            day="Monday",
            start=time(9, 0),
            end=time(10, 30)
        )
    
    def test_attendance_creation(self):
        """Тест создания записи о посещаемости"""
        attendance = Attendance.objects.create(
            Student=self.student,
            shcedule=self.schedule,
            status=True
        )
        self.assertEqual(attendance.Student, self.student)
        self.assertEqual(attendance.shcedule, self.schedule)
        self.assertTrue(attendance.status)


class ScheduleItemAPITest(APITestCase):
    """Тесты для API расписания"""
    
    def setUp(self):
        # Создаем программу и курс
        self.program = Program.objects.create(
            title="Computer Science",
            summary="CS Program"
        )
        self.course = Course.objects.create(
            title="Python Programming",
            code="CS101",
            credit=3,
            program=self.program
        )
        self.group = Group.objects.create(name="Group A")
        
        # Создаем пользователей разных ролей
        self.admin = User.objects.create_superuser(
            username="admin",
            password="admin123",
            email="admin@test.com"
        )
        
        self.lecturer = User.objects.create_user(
            username="lecturer",
            password="lecturer123",
            is_lecturer=True
        )
        
        self.student_user = User.objects.create_user(
            username="student",
            password="student123",
            is_student=True
        )
        self.student = Student.objects.create(
            student=self.student_user,
            level="Bachelor",
            group=self.group
        )
        
        # Создаем токены
        self.admin_token = Token.objects.create(user=self.admin)
        self.lecturer_token = Token.objects.create(user=self.lecturer)
        self.student_token = Token.objects.create(user=self.student_user)
        
        # Создаем тестовое расписание
        self.schedule = ScheduleItem.objects.create(
            course=self.course,
            group=self.group,
            order=1,
            day="Monday",
            start=time(9, 0),
            end=time(10, 30)
        )
        
        self.client = APIClient()
    
    def test_student_can_view_schedule(self):
        """Студент может просматривать расписание своей группы"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.get('/attendance/schedules/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_student_cannot_create_schedule(self):
        """Студент не может создавать расписание"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        data = {
            'course': self.course.id,
            'group': self.group.id,
            'order': 2,
            'day': 'Tuesday',
            'start': '11:00:00',
            'end': '12:30:00'
        }
        response = self.client.post('/attendance/schedules/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_can_create_schedule(self):
        """Администратор может создавать расписание"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        data = {
            'course': self.course.id,
            'group': self.group.id,
            'order': 2,
            'day': 'Tuesday',
            'start': '11:00:00',
            'end': '12:30:00'
        }
        response = self.client.post('/attendance/schedules/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_filter_schedule_by_day(self):
        """Фильтрация расписания по дню"""
        # Создаем расписание на другой день
        ScheduleItem.objects.create(
            course=self.course,
            group=self.group,
            order=1,
            day="Tuesday",
            start=time(9, 0),
            end=time(10, 30)
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get('/attendance/schedules/?day=Monday')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['day'], 'Monday')
    
    def test_my_schedule_endpoint(self):
        """Тест эндпоинта my_schedule для студента"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.get('/attendance/schedules/my_schedule/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class AttendanceAPITest(APITestCase):
    """Тесты для API посещаемости"""
    
    def setUp(self):
        # Создаем программу и курс
        self.program = Program.objects.create(
            title="Computer Science",
            summary="CS Program"
        )
        self.course = Course.objects.create(
            title="Python Programming",
            code="CS101",
            credit=3,
            program=self.program
        )
        self.group = Group.objects.create(name="Group A")
        
        # Создаем пользователей
        self.admin = User.objects.create_superuser(
            username="admin",
            password="admin123",
            email="admin@test.com"
        )
        
        self.lecturer = User.objects.create_user(
            username="lecturer",
            password="lecturer123",
            is_lecturer=True
        )
        
        self.student_user = User.objects.create_user(
            username="student",
            password="student123",
            is_student=True
        )
        self.student = Student.objects.create(
            student=self.student_user,
            level="Bachelor",
            group=self.group
        )
        
        # Создаем токены
        self.admin_token = Token.objects.create(user=self.admin)
        self.lecturer_token = Token.objects.create(user=self.lecturer)
        self.student_token = Token.objects.create(user=self.student_user)
        
        # Создаем расписание
        self.schedule = ScheduleItem.objects.create(
            course=self.course,
            group=self.group,
            order=1,
            day="Monday",
            start=time(9, 0),
            end=time(10, 30)
        )
        
        # Создаем запись о посещаемости
        self.attendance = Attendance.objects.create(
            Student=self.student,
            shcedule=self.schedule,
            status=True
        )
        
        self.client = APIClient()
    
    def test_student_can_view_own_attendance(self):
        """Студент может просматривать свою посещаемость"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.get('/attendance/attendances/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_student_cannot_update_attendance(self):
        """Студент не может обновлять посещаемость"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        data = {'status': False}
        response = self.client.patch(f'/attendance/attendances/{self.attendance.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_lecturer_can_update_attendance(self):
        """Преподаватель может обновлять посещаемость"""
        # Связываем преподавателя с курсом
        from course.models import CourseAllocation
        CourseAllocation.objects.create(
            lecturer=self.lecturer,
            courses=self.course
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.lecturer_token.key}')
        data = {'status': False}
        response = self.client.patch(f'/attendance/attendances/{self.attendance.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['status'])
    
    def test_my_attendance_endpoint(self):
        """Тест эндпоинта my_attendance для студента"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.get('/attendance/attendances/my_attendance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_statistics_endpoint(self):
        """Тест эндпоинта статистики"""
        # Создаем еще несколько записей
        Attendance.objects.create(
            Student=self.student,
            shcedule=self.schedule,
            status=False
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.get('/attendance/attendances/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('present', response.data)
        self.assertIn('absent', response.data)
        self.assertIn('attendance_rate', response.data)
    
    def test_bulk_update_attendance(self):
        """Тест массового обновления посещаемости"""
        # Создаем еще студентов
        student2_user = User.objects.create_user(
            username="student2",
            password="student123",
            is_student=True
        )
        student2 = Student.objects.create(
            student=student2_user,
            level="Bachelor",
            group=self.group
        )
        
        # Связываем преподавателя с курсом
        from course.models import CourseAllocation
        CourseAllocation.objects.create(
            lecturer=self.lecturer,
            courses=self.course
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.lecturer_token.key}')
        data = {
            'schedule_id': self.schedule.id,
            'attendances': [
                {'student_id': self.student.id, 'status': True},
                {'student_id': student2.id, 'status': False}
            ]
        }
        response = self.client.post('/attendance/attendances/bulk_update/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class PermissionsTest(APITestCase):
    """Тесты для проверки прав доступа"""
    
    def setUp(self):
        # Создаем пользователей
        self.admin = User.objects.create_superuser(
            username="admin",
            password="admin123",
            email="admin@test.com"
        )
        
        self.lecturer = User.objects.create_user(
            username="lecturer",
            password="lecturer123",
            is_lecturer=True
        )
        
        self.student_user = User.objects.create_user(
            username="student",
            password="student123",
            is_student=True
        )
        
        # Создаем токены
        self.admin_token = Token.objects.create(user=self.admin)
        self.lecturer_token = Token.objects.create(user=self.lecturer)
        self.student_token = Token.objects.create(user=self.student_user)
        
        self.client = APIClient()
    
    def test_unauthenticated_user_cannot_access(self):
        """Неавторизованный пользователь не может получить доступ"""
        response = self.client.get('/attendance/schedules/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_student_can_access(self):
        """Авторизованный студент может получить доступ"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        response = self.client.get('/attendance/schedules/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_authenticated_lecturer_can_access(self):
        """Авторизованный преподаватель может получить доступ"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.lecturer_token.key}')
        response = self.client.get('/attendance/schedules/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_authenticated_admin_can_access(self):
        """Авторизованный администратор может получить доступ"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get('/attendance/schedules/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
