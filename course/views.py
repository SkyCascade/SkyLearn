from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

import os
import xml.etree.ElementTree as ET
import zipfile
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django_filters.views import FilterView

from accounts.decorators import lecturer_required, student_required
from accounts.models import Student
from core.models import Semester
from course.filters import CourseAllocationFilter, ProgramFilter
from course.forms import (
    CourseAddForm,
    CourseAllocationForm,
    EditCourseAllocationForm,
    ProgramForm,
    UploadFormFile,
    UploadFormVideo,
    SCORMUploadForm,
)
from course.models import (
    Course,
    CourseAllocation,
    Program,
    Upload,
    UploadVideo,
    VideoProgress,
    SCORMPackage,
)
from result.models import TakenCourse


# ########################################################
# Program Views
# ########################################################


@method_decorator([login_required, lecturer_required], name="dispatch")
class ProgramFilterView(FilterView):
    filterset_class = ProgramFilter
    template_name = "course/program_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Programs"
        return context


@login_required
@lecturer_required
def program_add(request):
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save()
            messages.success(request, f"{program.title} program has been created.")
            return redirect("programs")
        messages.error(request, "Correct the error(s) below.")
    else:
        form = ProgramForm()
    return render(
        request, "course/program_add.html", {"title": "Add Program", "form": form}
    )


@login_required
def program_detail(request, pk):
    program = get_object_or_404(Program, pk=pk)
    courses = Course.objects.filter(program_id=pk).order_by("-year")
    credits = courses.aggregate(total_credits=Sum("credit"))
    paginator = Paginator(courses, 10)
    page = request.GET.get("page")
    courses = paginator.get_page(page)
    return render(
        request,
        "course/program_single.html",
        {
            "title": program.title,
            "program": program,
            "courses": courses,
            "credits": credits,
        },
    )


@login_required
@lecturer_required
def program_edit(request, pk):
    program = get_object_or_404(Program, pk=pk)
    if request.method == "POST":
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            program = form.save()
            messages.success(request, f"{program.title} program has been updated.")
            return redirect("programs")
        messages.error(request, "Correct the error(s) below.")
    else:
        form = ProgramForm(instance=program)
    return render(
        request, "course/program_add.html", {"title": "Edit Program", "form": form}
    )


@login_required
@lecturer_required
def program_delete(request, pk):
    program = get_object_or_404(Program, pk=pk)
    title = program.title
    program.delete()
    messages.success(request, f"Program {title} has been deleted.")
    return redirect("programs")


# ########################################################
# Course Views
# ########################################################

@login_required
def course_single(request, slug):
    course = get_object_or_404(Course, slug=slug)
    files = Upload.objects.filter(course__slug=slug)
    videos = UploadVideo.objects.filter(course__slug=slug)
    scorm_packages = SCORMPackage.objects.filter(course=course)
    lecturers = CourseAllocation.objects.filter(courses__pk=course.id)

    return render(
        request,
        "course/course_single.html",
        {
            "title": course.title,
            "course": course,
            "files": files,
            "videos": videos,
            "scorm_packages": scorm_packages,
            "lecturers": lecturers,
            "media_url": settings.MEDIA_URL,
        },
    )


@login_required
@lecturer_required
def course_add(request, pk):
    program = get_object_or_404(Program, pk=pk)
    if request.method == "POST":
        form = CourseAddForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(
                request, f"{course.title} ({course.code}) has been created."
            )
            return redirect("program_detail", pk=program.pk)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = CourseAddForm(initial={"program": program})
    return render(
        request,
        "course/course_add.html",
        {"title": "Add Course", "form": form, "program": program},
    )


@login_required
@lecturer_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == "POST":
        form = CourseAddForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            messages.success(
                request, f"{course.title} ({course.code}) has been updated."
            )
            return redirect("program_detail", pk=course.program.pk)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = CourseAddForm(instance=course)
    return render(
        request, "course/course_add.html", {"title": "Edit Course", "form": form}
    )


@login_required
@lecturer_required
def course_delete(request, slug):
    course = get_object_or_404(Course, slug=slug)
    title = course.title
    program_id = course.program.id
    course.delete()
    messages.success(request, f"Course {title} has been deleted.")
    return redirect("program_detail", pk=program_id)


# ########################################################
# Course Allocation Views
# ########################################################


def _unassign_lecturer_from_dropped_courses(lecturer, dropped_course_ids):
    """
    When a lecturer is no longer allocated a course (courses removed from
    their CourseAllocation, or the whole allocation is deleted), any
    TakenCourse rows still pointing that lecturer at one of those courses
    are now stale: the teacher a student sees, and the course list a
    lecturer sees, would otherwise silently disagree with what admin just
    set up. We clear (not delete) the lecturer on those rows so the
    enrollment/grades stay intact but no longer show the wrong teacher.
    """
    if not dropped_course_ids:
        return 0
    return TakenCourse.objects.filter(
        lecturer=lecturer, course_id__in=dropped_course_ids
    ).update(lecturer=None)


@method_decorator([login_required, lecturer_required], name="dispatch")
class CourseAllocationFormView(CreateView):
    form_class = CourseAllocationForm
    template_name = "course/course_allocation_form.html"

    def form_valid(self, form):
        lecturer = form.cleaned_data["lecturer"]
        selected_courses = form.cleaned_data["courses"]
        allocation, created = CourseAllocation.objects.get_or_create(lecturer=lecturer)

        previous_course_ids = set(allocation.courses.values_list("id", flat=True))
        new_course_ids = {c.id for c in selected_courses}
        dropped_course_ids = previous_course_ids - new_course_ids

        allocation.courses.set(selected_courses)
        _unassign_lecturer_from_dropped_courses(lecturer, dropped_course_ids)

        messages.success(
            self.request, f"Courses allocated to {lecturer.get_full_name} successfully."
        )
        return redirect("course_allocation_view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Assign Course"
        return context


@method_decorator([login_required, lecturer_required], name="dispatch")
class CourseAllocationFilterView(FilterView):
    filterset_class = CourseAllocationFilter
    template_name = "course/course_allocation_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Course Allocations"
        return context


@login_required
@lecturer_required
def edit_allocated_course(request, pk):
    allocation = get_object_or_404(CourseAllocation, pk=pk)
    if request.method == "POST":
        previous_course_ids = set(allocation.courses.values_list("id", flat=True))
        form = EditCourseAllocationForm(request.POST, instance=allocation)
        if form.is_valid():
            form.save()
            new_course_ids = set(allocation.courses.values_list("id", flat=True))
            dropped_course_ids = previous_course_ids - new_course_ids
            _unassign_lecturer_from_dropped_courses(
                allocation.lecturer, dropped_course_ids
            )
            messages.success(request, "Course allocation has been updated.")
            return redirect("course_allocation_view")
        messages.error(request, "Correct the error(s) below.")
    else:
        form = EditCourseAllocationForm(instance=allocation)
    return render(
        request,
        "course/course_allocation_form.html",
        {"title": "Edit Course Allocation", "form": form},
    )


@login_required
@lecturer_required
def deallocate_course(request, pk):
    allocation = get_object_or_404(CourseAllocation, pk=pk)
    course_ids = list(allocation.courses.values_list("id", flat=True))
    lecturer = allocation.lecturer
    allocation.delete()
    _unassign_lecturer_from_dropped_courses(lecturer, course_ids)
    messages.success(request, "Successfully deallocated courses.")
    return redirect("course_allocation_view")


# ########################################################
# File Upload Views
# ########################################################


@login_required
@lecturer_required
def handle_file_upload(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == "POST":
        form = UploadFormFile(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.course = course
            upload.save()
            messages.success(request, f"{upload.title} has been uploaded.")
            return redirect("course_detail", slug=slug)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = UploadFormFile()
    return render(
        request,
        "upload/upload_file_form.html",
        {"title": "File Upload", "form": form, "course": course},
    )

@login_required
@lecturer_required
def handle_scorm_upload(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == "POST":
        form = SCORMUploadForm(request.POST, request.FILES)

        if form.is_valid():
            scorm = form.save(commit=False)
            scorm.course = course

            uploaded_file = request.FILES["package"]

            # Check that the uploaded file is a ZIP file
            if not uploaded_file.name.lower().endswith(".zip"):
                messages.error(request, "Please upload a SCORM ZIP file.")
                return render(
                    request,
                    "scorm/scorm_upload.html",
                    {
                        "title": "Upload SCORM Package",
                        "form": form,
                        "course": course,
                    },
                )

            # Save the uploaded ZIP
            scorm.save()

            # Extract SCORM package
            package_dir = os.path.join(
                settings.MEDIA_ROOT,
                "scorm",
                str(scorm.id),
            )

            os.makedirs(package_dir, exist_ok=True)

            with zipfile.ZipFile(scorm.package.path, "r") as zip_ref:
                zip_ref.extractall(package_dir)

            # Find imsmanifest.xml
            manifest_path = None

            for root, dirs, files in os.walk(package_dir):
                if "imsmanifest.xml" in files:
                    manifest_path = os.path.join(
                        root,
                        "imsmanifest.xml",
                    )
                    break

            if not manifest_path:
                scorm.package.delete(save=False)
                scorm.delete()

                messages.error(
                    request,
                    "Invalid SCORM package. imsmanifest.xml was not found.",
                )

                return render(
                    request,
                    "scorm/scorm_upload.html",
                    {
                        "title": "Upload SCORM Package",
                        "form": form,
                        "course": course,
                    },
                )

                       # Find the actual SCORM launch file from imsmanifest.xml
            tree = ET.parse(manifest_path)
            root_element = tree.getroot()


            for resource in root_element.iter():
                if resource.tag.endswith("resource"):
                    scorm_type = resource.attrib.get(
                        "{http://www.adlnet.org/xsd/adlcp_rootv1p2}scormtype"
                    )

                    href = resource.attrib.get("href")

                    if scorm_type == "sco" and href:
                        launch_file = href
                        break

            if not launch_file:

                scorm.package.delete(save=False)
                scorm.delete()

                messages.error(
                    request,
                    "Invalid SCORM package. Launch file was not found in imsmanifest.xml.",
                )

                return render(
                    request,
                    "scorm/scorm_upload.html",
                    {
                        "title": "Upload SCORM Package",
                        "form": form,
                        "course": course,
                    },
                )
            if not launch_file:
                scorm.package.delete(save=False)
                scorm.delete()

                messages.error(
                    request,
                    "Invalid SCORM package. Launch file was not found in imsmanifest.xml.",
                )

                return render(
                    request,
                    "scorm/scorm_upload.html",
                    {
                        "title": "Upload SCORM Package",
                        "form": form,
                        "course": course,
                    },
                )

            # Manifest may be inside a subfolder.
            manifest_dir = os.path.dirname(manifest_path)

            relative_launch_path = os.path.relpath(
                os.path.join(manifest_dir, launch_file),
                package_dir,
            ).replace("\\", "/")

            scorm.launch_file = relative_launch_path
            scorm.save(update_fields=["launch_file"])

            messages.success(
                request,
                f"{scorm.title} has been uploaded successfully.",
            )

            return redirect("course_detail", slug=slug)

        messages.error(request, "Correct the error(s) below.")

    else:
        form = SCORMUploadForm()

    return render(
        request,
        "scorm/scorm_upload.html",
        {
            "title": "Upload SCORM Package",
            "form": form,
            "course": course,
        },
    )
@login_required
def launch_scorm(request, slug, scorm_id):
    course = get_object_or_404(Course, slug=slug)

    scorm = get_object_or_404(
        SCORMPackage,
        id=scorm_id,
        course=course,
    )

    return render(
        request,
        "scorm/scorm_player.html",
        {
            "title": scorm.title,
            "course": course,
            "scorm": scorm,
        },
    )


@login_required
@lecturer_required
def handle_file_edit(request, slug, file_id):
    course = get_object_or_404(Course, slug=slug)
    upload = get_object_or_404(Upload, pk=file_id)
    if request.method == "POST":
        form = UploadFormFile(request.POST, request.FILES, instance=upload)
        if form.is_valid():
            upload = form.save()
            messages.success(request, f"{upload.title} has been updated.")
            return redirect("course_detail", slug=slug)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = UploadFormFile(instance=upload)
    return render(
        request,
        "upload/upload_file_form.html",
        {"title": "Edit File", "form": form, "course": course},
    )


@login_required
@lecturer_required
def handle_file_delete(request, slug, file_id):
    upload = get_object_or_404(Upload, pk=file_id)
    title = upload.title
    upload.delete()
    messages.success(request, f"{title} has been deleted.")
    return redirect("course_detail", slug=slug)


# ########################################################
# Video Upload Views
# ########################################################

@login_required
def handle_video_single(request, slug, video_slug):
    course = get_object_or_404(
        Course,
        slug=slug,
    )

    video = get_object_or_404(
        UploadVideo,
        slug=video_slug,
        course=course,
    )

    progress = None

    if request.user.is_student:
        progress = VideoProgress.objects.filter(
            student=request.user,
            video=video,
        ).first()

    return render(
        request,
        "upload/video_single.html",
        {
            "video": video,
            "course": course,
            "progress": progress,
        },
    )

@login_required
@student_required
def save_video_progress(request, slug, video_slug):
    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "error": "POST request required.",
            },
            status=405,
        )

    course = get_object_or_404(
        Course,
        slug=slug,
    )

    video = get_object_or_404(
        UploadVideo,
        slug=video_slug,
        course=course,
    )

    try:
        import json

        data = json.loads(request.body)

        watched_seconds = float(
            data.get("watched_seconds", 0)
        )

        duration_seconds = float(
            data.get("duration_seconds", 0)
        )

        last_position = float(
            data.get("last_position", 0)
        )

        completed = bool(
            data.get("completed", False)
        )

    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid progress data.",
            },
            status=400,
        )

    if duration_seconds > 0:
        progress_percent = (
            watched_seconds / duration_seconds
        ) * 100
    else:
        progress_percent = 0

    progress_percent = max(
        0,
        min(progress_percent, 100),
    )

    if progress_percent >= 100:
        progress_percent = 100
        completed = True

    progress, created = VideoProgress.objects.get_or_create(
        student=request.user,
        video=video,
    )

    # Keep the highest actual watched coverage.
    if watched_seconds >= progress.watched_seconds:
        progress.watched_seconds = watched_seconds

    if duration_seconds > 0:
        progress.duration_seconds = duration_seconds

    progress.last_position = max(
        0,
        last_position,
    )

    progress.progress_percent = progress_percent

    if completed:
        progress.completed = True

    progress.save()

    return JsonResponse(
        {
            "success": True,
            "progress_percent": round(
                progress.progress_percent,
                2,
            ),
            "completed": progress.completed,
            "last_position": progress.last_position,
        }
    )


# ########################################################
# Video Upload Views
# ########################################################


@login_required
@lecturer_required
def handle_video_upload(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == "POST":
        form = UploadFormVideo(request.POST, request.FILES)

        if form.is_valid():
            video = form.save(commit=False)
            video.course = course
            video.save()

            messages.success(
                request,
                f"{video.title} has been added successfully."
            )

            return redirect("course_detail", slug=slug)

        messages.error(request, "Correct the error(s) below.")

    else:
        form = UploadFormVideo()

    return render(
        request,
        "upload/upload_video_form.html",
        {
            "title": "Video Upload",
            "form": form,
            "course": course,
        },
    )


@login_required
def handle_video_single(request, slug, video_slug):
    course = get_object_or_404(
        Course,
        slug=slug,
    )

    video = get_object_or_404(
        UploadVideo,
        slug=video_slug,
        course=course,
    )

    progress = None

    if request.user.is_student:
        progress = VideoProgress.objects.filter(
            student=request.user,
            video=video,
        ).first()

    return render(
        request,
        "upload/video_single.html",
        {
            "video": video,
            "course": course,
            "progress": progress,
        },
    )


@login_required
@student_required
def save_video_progress(request, slug, video_slug):
    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "error": "POST request required.",
            },
            status=405,
        )

    course = get_object_or_404(
        Course,
        slug=slug,
    )

    video = get_object_or_404(
        UploadVideo,
        slug=video_slug,
        course=course,
    )

    try:
        import json

        data = json.loads(request.body)

        watched_seconds = float(
            data.get("watched_seconds", 0)
        )

        duration_seconds = float(
            data.get("duration_seconds", 0)
        )

        last_position = float(
            data.get("last_position", 0)
        )

        completed = bool(
            data.get("completed", False)
        )

    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid progress data.",
            },
            status=400,
        )

    if duration_seconds > 0:
        progress_percent = (
            watched_seconds / duration_seconds
        ) * 100
    else:
        progress_percent = 0

    progress_percent = max(
        0,
        min(progress_percent, 100),
    )

    if progress_percent >= 100:
        progress_percent = 100
        completed = True

    progress, created = VideoProgress.objects.get_or_create(
        student=request.user,
        video=video,
    )

    if watched_seconds >= progress.watched_seconds:
        progress.watched_seconds = watched_seconds

    if duration_seconds > 0:
        progress.duration_seconds = duration_seconds

    progress.last_position = max(
        0,
        last_position,
    )

    progress.progress_percent = progress_percent

    if completed:
        progress.completed = True

    progress.save()

    return JsonResponse(
        {
            "success": True,
            "progress_percent": round(
                progress.progress_percent,
                2,
            ),
            "completed": progress.completed,
            "last_position": progress.last_position,
        }
    )


@login_required
@lecturer_required
def handle_video_edit(request, slug, video_slug):
    course = get_object_or_404(
        Course,
        slug=slug,
    )

    video = get_object_or_404(
        UploadVideo,
        slug=video_slug,
        course=course,
    )

    if request.method == "POST":
        form = UploadFormVideo(
            request.POST,
            request.FILES,
            instance=video,
        )

        if form.is_valid():
            video = form.save()

            messages.success(
                request,
                f"{video.title} has been updated.",
            )

            return redirect(
                "course_detail",
                slug=slug,
            )

        messages.error(
            request,
            "Correct the error(s) below.",
        )

    else:
        form = UploadFormVideo(
            instance=video,
        )

    return render(
        request,
        "upload/upload_video_form.html",
        {
            "title": "Edit Video",
            "form": form,
            "course": course,
        },
    )


@login_required
@lecturer_required
def handle_video_delete(request, slug, video_slug):
    video = get_object_or_404(
        UploadVideo,
        slug=video_slug,
        course__slug=slug,
    )

    title = video.title

    video.delete()

    messages.success(
        request,
        f"{title} has been deleted.",
    )

    return redirect(
        "course_detail",
        slug=slug,
    )

# ########################################################
# Course Registration Views
# ########################################################


@login_required
@student_required
def course_registration(request):
    if request.method == "POST":
        student = Student.objects.get(student__pk=request.user.id)
        ids = ()
        data = request.POST.copy()
        data.pop("csrfmiddlewaretoken", None)  # remove csrf_token
        for key in data.keys():
            ids = ids + (str(key),)
        for s in range(0, len(ids)):
            course = Course.objects.get(pk=ids[s])
            obj = TakenCourse.objects.create(student=student, course=course)
            obj.save()
        messages.success(request, "Courses registered successfully!")
        return redirect("course_registration")
    else:
        current_semester = Semester.objects.filter(is_current_semester=True).first()
        if not current_semester:
            messages.error(request, "No active semester found.")
            return render(request, "course/course_registration.html")

        # student = Student.objects.get(student__pk=request.user.id)
        student = get_object_or_404(Student, student__id=request.user.id)
        taken_courses = TakenCourse.objects.filter(student__student__id=request.user.id)
        t = ()
        for i in taken_courses:
            t += (i.course.pk,)

        courses = (
            Course.objects.filter(
                program__pk=student.program.id,
                level=student.level,
                semester=current_semester,
            )
            .exclude(id__in=t)
            .order_by("year")
        )
        all_courses = Course.objects.filter(
            level=student.level, program__pk=student.program.id
        )

        no_course_is_registered = False  # Check if no course is registered
        all_courses_are_registered = False

        registered_courses = Course.objects.filter(level=student.level).filter(id__in=t)
        if (
            registered_courses.count() == 0
        ):  # Check if number of registered courses is 0
            no_course_is_registered = True

        if registered_courses.count() == all_courses.count():
            all_courses_are_registered = True

        total_first_semester_credit = 0
        total_sec_semester_credit = 0
        total_registered_credit = 0
        for i in courses:
            if i.semester == "First":
                total_first_semester_credit += int(i.credit)
            if i.semester == "Second":
                total_sec_semester_credit += int(i.credit)
        for i in registered_courses:
            total_registered_credit += int(i.credit)
        context = {
            "is_calender_on": True,
            "all_courses_are_registered": all_courses_are_registered,
            "no_course_is_registered": no_course_is_registered,
            "current_semester": current_semester,
            "courses": courses,
            "total_first_semester_credit": total_first_semester_credit,
            "total_sec_semester_credit": total_sec_semester_credit,
            "registered_courses": registered_courses,
            "total_registered_credit": total_registered_credit,
            "student": student,
        }
        return render(request, "course/course_registration.html", context)


@login_required
@student_required
def course_drop(request):
    if request.method == "POST":
        student = get_object_or_404(Student, student__pk=request.user.id)
        course_ids = request.POST.getlist("course_ids")
        print("course_ids", course_ids)
        for course_id in course_ids:
            course = get_object_or_404(Course, pk=course_id)
            TakenCourse.objects.filter(student=student, course=course).delete()
        messages.success(request, "Courses dropped successfully!")
        return redirect("course_registration")


# ########################################################
# User Course List View
# ########################################################


@login_required
def user_course_list(request):
    if request.user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=request.user.id)
        return render(request, "course/user_course_list.html", {"courses": courses})

    if request.user.is_student:
        student = get_object_or_404(Student, student__pk=request.user.id)
        taken_courses = TakenCourse.objects.filter(student=student)
        return render(
            request,
            "course/user_course_list.html",
            {"student": student, "taken_courses": taken_courses},
        )

    # For other users
    return render(request, "course/user_course_list.html")
