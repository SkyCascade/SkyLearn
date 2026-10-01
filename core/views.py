from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from accounts.decorators import (
    admin_required,
    lecturer_required,
    student_required,
)
from accounts.models import User, Student

from course.models import Course, CourseAllocation, Upload, UploadVideo, VideoProgress
from result.models import TakenCourse
from quiz.models import Quiz, Sitting
from gamification.models import StudentXP, StudentBadge, LearningStreak, QuizXPRecord
from gamification.services import get_level_info
from .forms import SessionForm, SemesterForm, NewsAndEventsForm
from .models import NewsAndEvents, ActivityLog, Session, Semester


# ########################################################
# News & Events
# ########################################################
@login_required
def home_view(request):
    items = NewsAndEvents.objects.all().order_by("-updated_date")
    context = {
        "title": "News & Events",
        "items": items,
    }
    return render(request, "core/index.html", context)


@login_required
@admin_required
def dashboard_view(request):
    logs = ActivityLog.objects.all().order_by("-created_at")[:10]
    gender_count = Student.get_gender_count()
    context = {
        "student_count": User.objects.get_student_count(),
        "lecturer_count": User.objects.get_lecturer_count(),
        "superuser_count": User.objects.get_superuser_count(),
        "males_count": gender_count["M"],
        "females_count": gender_count["F"],
        "logs": logs,
    }
    return render(request, "core/dashboard.html", context)

@login_required
@lecturer_required
def lecturer_dashboard_view(request):
    lecturer = request.user

    # Courses assigned to this lecturer
    courses = Course.objects.filter(
        allocated_course__lecturer=lecturer
    ).distinct()

    # Programs associated with the lecturer's courses
    programs = courses.values_list(
        "program",
        flat=True
    ).distinct()

    # Students belonging to those programs
    students = Student.objects.filter(
        program__in=programs
    ).select_related(
        "student",
        "program"
    ).distinct()

    student_count = students.count()

    # Materials uploaded to lecturer's courses
    material_count = Upload.objects.filter(
        course__in=courses
    ).count()

    video_count = UploadVideo.objects.filter(
        course__in=courses
    ).count()

    total_materials = material_count + video_count

    # Quizzes/assessments belonging to lecturer's courses
    assessment_count = Quiz.objects.filter(
        course__in=courses
    ).count()

    # Course enrollment data for chart
    course_enrollment = []

    for course in courses:
        enrollment = TakenCourse.objects.filter(
            course=course
        ).count()

        course_enrollment.append({
            "name": course.code,
            "students": enrollment,
        })

    # Average performance per course
    course_performance = []

    for course in courses:
        average = TakenCourse.objects.filter(
            course=course
        ).aggregate(
            avg=Avg("total")
        )["avg"]

        course_performance.append({
            "name": course.code,
            "average": round(float(average), 2) if average else 0,
        })

    # --------------------------------------------------
    # Student progress
    # --------------------------------------------------

    # Student profiles don't carry a confirmed field back to User in this
    # codebase, but the reverse accessor "student" (used elsewhere as
    # request.user.student) is confirmed, so go via User instead of
    # guessing the forward field name on Student.
    user_by_student_id = {
        u.student.id: u
        for u in User.objects.filter(student__in=students).select_related("student")
    }

    student_progress = []

    for student in students:

        taken_courses = TakenCourse.objects.filter(
            student=student,
            course__in=courses
        ).select_related("course")

        student_user = user_by_student_id.get(student.id)

        progress_data = []

        for taken in taken_courses:
            video_total = UploadVideo.objects.filter(course=taken.course).count()
            video_completed = (
                VideoProgress.objects.filter(
                    student=student_user, video__course=taken.course, completed=True
                ).count()
                if student_user else 0
            )
            video_percent = round(
                (video_completed / video_total) * 100, 1
            ) if video_total else 0

            course_quizzes = Quiz.objects.filter(course=taken.course)
            quiz_scores = list(
                QuizXPRecord.objects.filter(
                    student=student_user, quiz__in=course_quizzes
                ).values_list("best_percent", flat=True)
            ) if student_user else []
            quiz_average = round(
                sum(quiz_scores) / len(quiz_scores), 1
            ) if quiz_scores else None

            progress_data.append({
                "course": taken.course,
                "assignment": taken.assignment,
                "mid_exam": taken.mid_exam,
                "quiz": taken.quiz,
                "attendance": taken.attendance,
                "final_exam": taken.final_exam,
                "total": taken.total,
                "grade": taken.grade,
                "video_progress_percent": video_percent,
                "quiz_average": quiz_average,
            })

        total_xp = 0
        badge_count = 0
        if student_user:
            xp_record = StudentXP.objects.filter(student=student_user).first()
            total_xp = xp_record.total_xp if xp_record else 0
            badge_count = StudentBadge.objects.filter(student=student_user).count()

        student_progress.append({
            "student": student,
            "student_name": student_user.get_full_name if student_user else str(student),
            "courses": progress_data,
            "total_xp": total_xp,
            "badge_count": badge_count,
        })

    context = {
        "title": "Lecturer Dashboard",
        "lecturer": lecturer,
        "courses": courses,

        # Statistics
        "course_count": courses.count(),
        "student_count": student_count,
        "material_count": total_materials,
        "assessment_count": assessment_count,

        # Charts
        "course_enrollment": course_enrollment,
        "course_performance": course_performance,

        # Students and progress
        "students": students,
        "student_progress": student_progress,
    }

    return render(
        request,
        "core/lecturer_dashboard.html",
        context,
    )


@login_required
@student_required
def student_dashboard_view(request):
    student = request.user.student

    # Courses registered by the student
    taken_courses = TakenCourse.objects.filter(
        student=student
    ).select_related("course")

    # Basic statistics
    course_count = taken_courses.count()

    completed_count = taken_courses.filter(
        total__gt=0
    ).count()

    pending_count = taken_courses.filter(
        total=0
    ).count()

    # Average marks
    average_score = taken_courses.aggregate(
        average=Avg("total")
    )["average"]

    average_score = round(
        float(average_score), 2
    ) if average_score is not None else 0

    # GPA / CGPA
    gpa = 0
    cgpa = 0

    if taken_courses.exists():
        first_course = taken_courses.first()
        gpa = first_course.calculate_gpa()
        cgpa = first_course.calculate_cgpa()

    # Course performance
    course_performance = []

    for taken_course in taken_courses:
        course_performance.append({
            "name": taken_course.course.code,
            "score": float(taken_course.total),
        })

    enrolled_course_ids = taken_courses.values_list("course_id", flat=True)

    # --------------------------------------------------
    # Gamification: XP / level / streak / badges
    # --------------------------------------------------

    xp_record = StudentXP.objects.filter(student=request.user).first()
    total_xp = xp_record.total_xp if xp_record else 0
    level_info = get_level_info(total_xp)

    streak = LearningStreak.objects.filter(student=request.user).first()

    earned_badges = StudentBadge.objects.filter(
        student=request.user
    ).select_related("badge").order_by("-earned_at")

    # --------------------------------------------------
    # Video learning progress (across enrolled courses)
    # --------------------------------------------------

    total_videos = UploadVideo.objects.filter(
        course_id__in=enrolled_course_ids
    ).count()

    completed_videos = VideoProgress.objects.filter(
        student=request.user,
        video__course_id__in=enrolled_course_ids,
        completed=True,
    ).count()

    video_progress_percent = round(
        (completed_videos / total_videos) * 100, 1
    ) if total_videos else 0

    # --------------------------------------------------
    # Assigned quizzes (per-quiz status, not just a count)
    # --------------------------------------------------

    quizzes = Quiz.objects.filter(
        course_id__in=enrolled_course_ids
    ).select_related("course")

    quiz_records = {
        r.quiz_id: r
        for r in QuizXPRecord.objects.filter(student=request.user, quiz__in=quizzes)
    }
    in_progress_quiz_ids = set(
        Sitting.objects.filter(user=request.user, quiz__in=quizzes, complete=False)
        .values_list("quiz_id", flat=True)
    )

    quiz_status = []
    for quiz in quizzes:
        record = quiz_records.get(quiz.id)
        quiz_status.append({
            "quiz": quiz,
            "course": quiz.course,
            "attempted": record is not None,
            "best_percent": record.best_percent if record else None,
            "in_progress": quiz.id in in_progress_quiz_ids,
        })

    quiz_count = quizzes.count()

    context = {
        "title": "Student Dashboard",
        "student": student,
        "taken_courses": taken_courses,
        "course_count": course_count,
        "completed_count": completed_count,
        "pending_count": pending_count,
        "average_score": average_score,
        "gpa": gpa,
        "cgpa": cgpa,
        "quiz_count": quiz_count,
        "course_performance": course_performance,

        # Gamification
        "level_info": level_info,
        "streak": streak,
        "earned_badges": earned_badges,

        # Video progress
        "total_videos": total_videos,
        "completed_videos": completed_videos,
        "video_progress_percent": video_progress_percent,

        # Assigned quizzes
        "quiz_status": quiz_status,
    }

    return render(
        request,
        "core/student_dashboard.html",
        context,
    )

@login_required
def post_add(request):
    if request.method == "POST":
        form = NewsAndEventsForm(request.POST)
        title = form.cleaned_data.get("title", "Post") if form.is_valid() else None
        if form.is_valid():
            form.save()
            messages.success(request, f"{title} has been uploaded.")
            return redirect("home")
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = NewsAndEventsForm()
    return render(request, "core/post_add.html", {"title": "Add Post", "form": form})


@login_required
@lecturer_required
def edit_post(request, pk):
    instance = get_object_or_404(NewsAndEvents, pk=pk)
    if request.method == "POST":
        form = NewsAndEventsForm(request.POST, instance=instance)
        title = form.cleaned_data.get("title", "Post") if form.is_valid() else None
        if form.is_valid():
            form.save()
            messages.success(request, f"{title} has been updated.")
            return redirect("home")
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = NewsAndEventsForm(instance=instance)
    return render(request, "core/post_add.html", {"title": "Edit Post", "form": form})


@login_required
@lecturer_required
def delete_post(request, pk):
    post = get_object_or_404(NewsAndEvents, pk=pk)
    post_title = post.title
    post.delete()
    messages.success(request, f"{post_title} has been deleted.")
    return redirect("home")


# ########################################################
# Session
# ########################################################
@login_required
@lecturer_required
def session_list_view(request):
    """Show list of all sessions"""
    sessions = Session.objects.all().order_by("-is_current_session", "-session")
    return render(request, "core/session_list.html", {"sessions": sessions})


@login_required
@lecturer_required
def session_add_view(request):
    """Add a new session"""
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("is_current_session"):
                unset_current_session()
            form.save()
            messages.success(request, "Session added successfully.")
            return redirect("session_list")
    else:
        form = SessionForm()
    return render(request, "core/session_update.html", {"form": form})


@login_required
@lecturer_required
def session_update_view(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == "POST":
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            if form.cleaned_data.get("is_current_session"):
                unset_current_session()
            form.save()
            messages.success(request, "Session updated successfully.")
            return redirect("session_list")
    else:
        form = SessionForm(instance=session)
    return render(request, "core/session_update.html", {"form": form})


@login_required
@lecturer_required
def session_delete_view(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if session.is_current_session:
        messages.error(request, "You cannot delete the current session.")
    else:
        session.delete()
        messages.success(request, "Session successfully deleted.")
    return redirect("session_list")


def unset_current_session():
    """Unset current session"""
    current_session = Session.objects.filter(is_current_session=True).first()
    if current_session:
        current_session.is_current_session = False
        current_session.save()


# ########################################################
# Semester
# ########################################################
@login_required
@lecturer_required
def semester_list_view(request):
    semesters = Semester.objects.all().order_by("-is_current_semester", "-semester")
    return render(request, "core/semester_list.html", {"semesters": semesters})


@login_required
@lecturer_required
def semester_add_view(request):
    if request.method == "POST":
        form = SemesterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("is_current_semester"):
                unset_current_semester()
                unset_current_session()
            form.save()
            messages.success(request, "Semester added successfully.")
            return redirect("semester_list")
    else:
        form = SemesterForm()
    return render(request, "core/semester_update.html", {"form": form})


@login_required
@lecturer_required
def semester_update_view(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if request.method == "POST":
        form = SemesterForm(request.POST, instance=semester)
        if form.is_valid():
            if form.cleaned_data.get("is_current_semester"):
                unset_current_semester()
                unset_current_session()
            form.save()
            messages.success(request, "Semester updated successfully!")
            return redirect("semester_list")
    else:
        form = SemesterForm(instance=semester)
    return render(request, "core/semester_update.html", {"form": form})


@login_required
@lecturer_required
def semester_delete_view(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if semester.is_current_semester:
        messages.error(request, "You cannot delete the current semester.")
    else:
        semester.delete()
        messages.success(request, "Semester successfully deleted.")
    return redirect("semester_list")


def unset_current_semester():
    """Unset current semester"""
    current_semester = Semester.objects.filter(is_current_semester=True).first()
    if current_semester:
        current_semester.is_current_semester = False
        current_semester.save()