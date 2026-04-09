from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'faculty'):
            try:
                faculty = request.user.faculty
            except Exception:
                faculty = None

            if faculty and faculty.must_change_password:
                allowed_paths = {
                    reverse('force_password_change'),
                    reverse('logout'),
                    reverse('login'),
                }
                if request.path not in allowed_paths and not request.path.startswith('/static/'):
                    return redirect('force_password_change')

        return self.get_response(request)
