from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from accounts.decorators import admin_required, lecturer_required
from accounts.models import User, Student
from .forms import ProgramCycleForm, CohortForm, NewsAndEventsForm
from .models import NewsAndEvents, ActivityLog, ProgramCycle, Cohort


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

    # Count active courses (current cohort)
    from course.models import Course

    current_cohort = Cohort.objects.filter(is_current_cohort=True).first()
    if current_cohort:
        active_courses_count = Course.objects.filter(
            semester=current_cohort.cohort
        ).count()
    else:
        active_courses_count = 0

    # Count recent registrations (last 30 days)
    from accounts.models import User
    from django.utils import timezone
    from datetime import timedelta

    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_registrations_count = User.objects.filter(
        date_joined__gte=thirty_days_ago
    ).count()

    context = {
        "student_count": User.objects.get_student_count(),
        "lecturer_count": User.objects.get_lecturer_count(),
        "superuser_count": User.objects.get_superuser_count(),
        "active_courses_count": active_courses_count,
        "recent_registrations_count": recent_registrations_count,
        "males_count": gender_count["M"],
        "females_count": gender_count["F"],
        "logs": logs,
    }
    return render(request, "core/dashboard.html", context)


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
# Program Cycle (formerly Session)
# ########################################################
@login_required
@lecturer_required
def program_cycle_list_view(request):
    """Show list of all program cycles"""
    program_cycles = ProgramCycle.objects.all().order_by(
        "-is_current_program_cycle", "-program_cycle"
    )
    return render(
        request, "core/program_cycle_list.html", {"program_cycles": program_cycles}
    )


@login_required
@lecturer_required
def program_cycle_add_view(request):
    """Add a new program cycle"""
    if request.method == "POST":
        form = ProgramCycleForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("is_current_program_cycle"):
                unset_current_program_cycle()
            form.save()
            messages.success(request, "Program cycle added successfully.")
            return redirect("program_cycle_list")
    else:
        form = ProgramCycleForm()
    return render(request, "core/program_cycle_update.html", {"form": form})


@login_required
@lecturer_required
def program_cycle_update_view(request, pk):
    program_cycle = get_object_or_404(ProgramCycle, pk=pk)
    if request.method == "POST":
        form = ProgramCycleForm(request.POST, instance=program_cycle)
        if form.is_valid():
            if form.cleaned_data.get("is_current_program_cycle"):
                unset_current_program_cycle()
            form.save()
            messages.success(request, "Program cycle updated successfully.")
            return redirect("program_cycle_list")
    else:
        form = ProgramCycleForm(instance=program_cycle)
    return render(request, "core/program_cycle_update.html", {"form": form})


@login_required
@lecturer_required
def program_cycle_delete_view(request, pk):
    program_cycle = get_object_or_404(ProgramCycle, pk=pk)
    if program_cycle.is_current_program_cycle:
        messages.error(request, "You cannot delete the current program cycle.")
    else:
        program_cycle.delete()
        messages.success(request, "Program cycle successfully deleted.")
    return redirect("program_cycle_list")


def unset_current_program_cycle():
    """Unset current program cycle"""
    current = ProgramCycle.objects.filter(is_current_program_cycle=True).first()
    if current:
        current.is_current_program_cycle = False
        current.save()


# Keep backward-compatible aliases
session_list_view = program_cycle_list_view
session_add_view = program_cycle_add_view
session_update_view = program_cycle_update_view
session_delete_view = program_cycle_delete_view
unset_current_session = unset_current_program_cycle


# ########################################################
# Cohort (formerly Semester)
# ########################################################
@login_required
@lecturer_required
def cohort_list_view(request):
    cohorts = Cohort.objects.all().order_by("-is_current_cohort", "-cohort")
    return render(request, "core/cohort_list.html", {"cohorts": cohorts})


@login_required
@lecturer_required
def cohort_add_view(request):
    if request.method == "POST":
        form = CohortForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("is_current_cohort"):
                unset_current_cohort()
                unset_current_program_cycle()
            form.save()
            messages.success(request, "Cohort added successfully.")
            return redirect("cohort_list")
    else:
        form = CohortForm()
    return render(request, "core/cohort_update.html", {"form": form})


@login_required
@lecturer_required
def cohort_update_view(request, pk):
    cohort = get_object_or_404(Cohort, pk=pk)
    if request.method == "POST":
        form = CohortForm(request.POST, instance=cohort)
        if form.is_valid():
            if form.cleaned_data.get("is_current_cohort"):
                unset_current_cohort()
                unset_current_program_cycle()
            form.save()
            messages.success(request, "Cohort updated successfully!")
            return redirect("cohort_list")
    else:
        form = CohortForm(instance=cohort)
    return render(request, "core/cohort_update.html", {"form": form})


@login_required
@lecturer_required
def cohort_delete_view(request, pk):
    cohort = get_object_or_404(Cohort, pk=pk)
    if cohort.is_current_cohort:
        messages.error(request, "You cannot delete the current cohort.")
    else:
        cohort.delete()
        messages.success(request, "Cohort successfully deleted.")
    return redirect("cohort_list")


def unset_current_cohort():
    """Unset current cohort"""
    current_cohort = Cohort.objects.filter(is_current_cohort=True).first()
    if current_cohort:
        current_cohort.is_current_cohort = False
        current_cohort.save()


# Keep backward-compatible aliases
semester_list_view = cohort_list_view
semester_add_view = cohort_add_view
semester_update_view = cohort_update_view
semester_delete_view = cohort_delete_view
unset_current_semester = unset_current_cohort
