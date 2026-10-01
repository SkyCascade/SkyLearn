def post_save_account_receiver(instance=None, created=False, *args, **kwargs):
    """
    Account creation is handled by the admin forms and views.
    The username and password entered by the admin must not be replaced.
    """
    pass