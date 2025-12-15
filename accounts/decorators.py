from django.shortcuts import redirect
from django.contrib import messages

def admin_required(
    function=None,
    redirect_to="/",
):
    """
    Decorator for views that checks that the logged-in user is a superuser,
    redirects to the specified URL if necessary.
    """

    # Define the test function: checks if the user is active and a superuser
    def test_func(user):
        return user.is_active and user.is_superuser

    # Define the wrapper function to handle the response
    def wrapper(request, *args, **kwargs):
        if test_func(request.user):
            # Call the original function if the user passes the test
            return function(request, *args, **kwargs) if function else None
        # Redirect to the specified URL if the user fails the test
        return redirect(redirect_to)

    return wrapper if function else test_func


def lecturer_required(
    function=None,
    redirect_to="/",
):
    """
    Decorator for views that checks that the logged-in user is a superuser,
    redirects to the specified URL if necessary.
    """

    # Define the test function: checks if the user is active and a superuser
    def test_func(user):
        return user.is_active and user.is_lecturer or user.is_superuser

    # Define the wrapper function to handle the response
    def wrapper(request, *args, **kwargs):
        if test_func(request.user):
            # Call the original function if the user passes the test
            return function(request, *args, **kwargs) if function else None
        # Redirect to the specified URL if the user fails the test
        return redirect(redirect_to)

    return wrapper if function else test_func


def student_required(
    function=None,
    redirect_to="/",
):
    """
    Decorator for views that checks that the logged-in user is a superuser,
    redirects to the specified URL if necessary.
    """

    # Define the test function: checks if the user is active and a superuser
    def test_func(user):
        return user.is_active and user.is_student or user.is_superuser

    # Define the wrapper function to handle the response
    def wrapper(request, *args, **kwargs):
        if test_func(request.user):
            # Call the original function if the user passes the test
            return function(request, *args, **kwargs) if function else None
        # Redirect to the specified URL if the user fails the test
        return redirect(redirect_to)

    return wrapper if function else test_func

def department_head_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.is_dep_head:
            messages.error(request, "Access denied")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper
