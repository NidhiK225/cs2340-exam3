# accounts/decorators.py
from django.contrib.auth.decorators import user_passes_test

def recruiter_required(view_func):
    decorated = user_passes_test(lambda u: u.is_authenticated and (getattr(u, "is_recruiter", False) or getattr(u, "is_superuser", False)))(view_func)
    return decorated

def roadtripper_required(view_func):
    decorated = user_passes_test(lambda u: u.is_authenticated and (getattr(u, "is_roadTripper", False) or getattr(u, "is_superuser", False)))(view_func)
    return decorated