from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import LoginForm
from .models import Faculty, Notice
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def _get_home_announcements(limit=8):
    return Notice.objects.filter(is_published=True).order_by('-published_at', '-created_at')[:limit]

@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    """Faculty/Admin Login with role gating to avoid redirect loops"""
    if request.user.is_authenticated:
        # Only redirect if the user has a valid role
        if request.user.is_staff or hasattr(request.user, 'faculty'):
            if hasattr(request.user, 'faculty') and request.user.faculty.must_change_password:
                return redirect('force_password_change')
            return redirect('dashboard')
        else:
            # Logout users without a role to break redirect loops
            logout(request)
            form = LoginForm()
            form.add_error(None, 'Your account is not assigned a role. Please contact admin.')
            return render(request, 'auth/login.html', {
                'form': form,
                'announcements': _get_home_announcements(),
            })
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Gate by role before logging in to avoid loops
                if user.is_staff or hasattr(user, 'faculty'):
                    login(request, user)
                    if hasattr(user, 'faculty') and user.faculty.must_change_password:
                        return redirect('force_password_change')
                    return redirect('dashboard')
                else:
                    form.add_error(None, 'Your account has no assigned role. Contact admin.')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {
        'form': form,
        'announcements': _get_home_announcements(),
    })

def logout_view(request):
    """Logout"""
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def force_password_change(request):
    """Force faculty to change password on first login after admin set/reset."""
    if not hasattr(request.user, 'faculty'):
        return redirect('dashboard')

    faculty = request.user.faculty
    if not faculty.must_change_password:
        return redirect('dashboard')

    error = None
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not new_password or not confirm_password:
            error = 'Please fill both password fields.'
        elif new_password != confirm_password:
            error = 'Passwords do not match.'
        else:
            try:
                validate_password(new_password, request.user)
            except ValidationError as exc:
                error = ' '.join(exc.messages)

        if not error:
            request.user.set_password(new_password)
            request.user.save()
            faculty.must_change_password = False
            faculty.save()
            logout(request)
            return redirect('login')

    return render(request, 'auth/force_password_change.html', {
        'error': error,
    })

@login_required(login_url='login')
def check_role(request):
    """Check user role and redirect accordingly"""
    if request.user.is_staff:
        return 'admin'
    elif hasattr(request.user, 'faculty'):
        return 'faculty'
    return 'unknown'

@login_required(login_url='login')
def is_admin(request):
    """Check if user is admin"""
    return request.user.is_staff

@login_required(login_url='login')
def is_faculty(request):
    """Check if user is faculty"""
    return hasattr(request.user, 'faculty')
