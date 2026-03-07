from .utils import (
    generate_student_credentials,
    generate_lecturer_credentials,
    generate_password,
    send_new_account_email,
)


def post_save_account_receiver(instance=None, created=False, *args, **kwargs):
    """
    Send email notification with auto-generated password
    """
    if created:
        if instance.is_student:
            # Only generate username if not already set (self-registered users set their own)
            if not instance.username or instance.username.startswith("STU-"):
                username, password = generate_student_credentials()
                instance.username = username
            else:
                # User already has a username, just generate password
                password = generate_password()

            instance.set_password(password)
            instance.save()
            # Send email with the generated credentials
            send_new_account_email(instance, password)

        if instance.is_lecturer:
            username, password = generate_lecturer_credentials()
            instance.username = username
            instance.set_password(password)
            instance.save()
            # Send email with the generated credentials
            send_new_account_email(instance, password)
