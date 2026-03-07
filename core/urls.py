from django.urls import path

from .views import (
    home_view,
    post_add,
    edit_post,
    delete_post,
    program_cycle_list_view,
    program_cycle_add_view,
    program_cycle_update_view,
    program_cycle_delete_view,
    cohort_list_view,
    cohort_add_view,
    cohort_update_view,
    cohort_delete_view,
    dashboard_view,
)


urlpatterns = [
    # Accounts url
    path("", home_view, name="home"),
    path("add_item/", post_add, name="add_item"),
    path("item/<int:pk>/edit/", edit_post, name="edit_post"),
    path("item/<int:pk>/delete/", delete_post, name="delete_post"),
    # Program Cycle (formerly Session) urls
    path("program-cycle/", program_cycle_list_view, name="program_cycle_list"),
    path("program-cycle/add/", program_cycle_add_view, name="add_program_cycle"),
    path(
        "program-cycle/<int:pk>/edit/",
        program_cycle_update_view,
        name="edit_program_cycle",
    ),
    path(
        "program-cycle/<int:pk>/delete/",
        program_cycle_delete_view,
        name="delete_program_cycle",
    ),
    # Backward-compatible aliases
    path("session/", program_cycle_list_view, name="session_list"),
    path("session/add/", program_cycle_add_view, name="add_session"),
    path("session/<int:pk>/edit/", program_cycle_update_view, name="edit_session"),
    path("session/<int:pk>/delete/", program_cycle_delete_view, name="delete_session"),
    # Cohort (formerly Semester) urls
    path("cohort/", cohort_list_view, name="cohort_list"),
    path("cohort/add/", cohort_add_view, name="add_cohort"),
    path("cohort/<int:pk>/edit/", cohort_update_view, name="edit_cohort"),
    path("cohort/<int:pk>/delete/", cohort_delete_view, name="delete_cohort"),
    # Backward-compatible aliases
    path("semester/", cohort_list_view, name="semester_list"),
    path("semester/add/", cohort_add_view, name="add_semester"),
    path("semester/<int:pk>/edit/", cohort_update_view, name="edit_semester"),
    path("semester/<int:pk>/delete/", cohort_delete_view, name="delete_semester"),
    # Dashboard
    path("dashboard/", dashboard_view, name="dashboard"),
]
