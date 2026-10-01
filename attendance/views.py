import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import lecturer_required, student_required
from course.models import Course, CourseAllocation
from result.models import TakenCourse

from .models import AttendanceRecord, AttendanceSession, LectureSlot
from .services import get_attendance_stats_for_courses


def _lecturer_can_manage_course(user, course):
    """Same rule quiz/views.py uses: superuser, or actually allocated the course."""
    if user.is_superuser:
        return True
    return CourseAllocation.objects.filter(lecturer=user, courses=course).exists()


def _require_course_access(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not _lecturer_can_manage_course(request.user, course):
        messages.error(
            request,
            "You are not allocated to this course, so you can't manage its attendance.",
        )
        return course, False
    return course, True


@login_required
@lecturer_required
def session_list(request, slug):
    course, allowed = _require_course_access(request, slug)
    if not allowed:
        return redirect("lecturer_dashboard")

    sessions = AttendanceSession.objects.filter(course=course).select_related("lecture_slot")
    slots = LectureSlot.objects.filter(course=course, is_active=True)

    return render(
        request,
        "attendance/session_list.html",
        {"course": course, "sessions": sessions, "slots": slots},
    )


@login_required
@lecturer_required
def session_create(request, slug):
    course, allowed = _require_course_access(request, slug)
    if not allowed:
        return redirect("lecturer_dashboard")

    slots = LectureSlot.objects.filter(course=course, is_active=True)

    if request.method == "POST":
        date_str = request.POST.get("date")
        slot_id = request.POST.get("lecture_slot")
        topic = request.POST.get("topic", "").strip()

        try:
            session_date = datetime.date.fromisoformat(date_str)
        except (TypeError, ValueError):
            messages.error(request, "Please provide a valid date.")
            return render(
                request, "attendance/session_create.html",
                {"course": course, "slots": slots},
            )

        lecture_slot = None
        if slot_id:
            lecture_slot = get_object_or_404(LectureSlot, pk=slot_id, course=course)

        session, created = AttendanceSession.objects.get_or_create(
            course=course, date=session_date, lecture_slot=lecture_slot,
            defaults={"topic": topic, "created_by": request.user},
        )
        if not created:
            messages.info(request, "A session for that date/slot already exists — opening it.")

        return redirect("attendance_session_mark", slug=course.slug, session_id=session.id)

    return render(
        request, "attendance/session_create.html",
        {"course": course, "slots": slots},
    )


@login_required
@lecturer_required
def session_mark(request, slug, session_id):
    course, allowed = _require_course_access(request, slug)
    if not allowed:
        return redirect("lecturer_dashboard")

    session = get_object_or_404(AttendanceSession, pk=session_id, course=course)

    enrolled_students = [
        tc.student for tc in TakenCourse.objects.filter(course=course).select_related("student")
    ]

    existing = {
        r.student_id: r.status
        for r in AttendanceRecord.objects.filter(session=session)
    }

    if request.method == "POST":
        present_ids = set(request.POST.getlist("present"))
        for student in enrolled_students:
            status = (
                AttendanceRecord.PRESENT
                if str(student.id) in present_ids
                else AttendanceRecord.ABSENT
            )
            AttendanceRecord.objects.update_or_create(
                session=session, student=student,
                defaults={"status": status, "marked_by": request.user},
            )
        messages.success(request, "Attendance saved.")
        return redirect("attendance_session_list", slug=course.slug)

    roster = [
        {"student": student, "present": existing.get(student.id, AttendanceRecord.ABSENT) == AttendanceRecord.PRESENT}
        for student in enrolled_students
    ]

    return render(
        request, "attendance/session_mark.html",
        {"course": course, "session": session, "roster": roster},
    )


@login_required
@student_required
def my_attendance(request):
    student = request.user.student
    courses = [tc.course for tc in TakenCourse.objects.filter(student=student).select_related("course")]
    stats = get_attendance_stats_for_courses(student, courses)

    return render(request, "attendance/my_attendence.html", {"stats": stats})
@login_required
@lecturer_required
def lecturer_home(request):
    if request.user.is_superuser:
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(
            allocated_course__lecturer=request.user
        ).distinct()
    return render(request, "attendance/lecturer_home.html", {"courses": courses})