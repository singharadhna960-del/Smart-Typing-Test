import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from .models import User, EmailVerification, PasswordReset

#HOME
def index(request):
    return render(request, 'index.html')

# REGISTER
def register(request):
    if request.method == "POST":
        username = request.POST['username'].strip()
        email = request.POST['email'].strip().lower()
        password = request.POST['password']

        # check existing user
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('register')

        # create user with hashed password
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_verified=False
        )

        # create verification token
        token = str(uuid.uuid4())

        EmailVerification.objects.create(
            user=user,
            token=token
        )

        print("Verification Link: http://127.0.0.1:8000/verify/?token=" + token)

        messages.success(request, "Check console for verification link!")
        return redirect('login')

    return render(request, 'register.html')


#LOGIN
def login(request):
    if request.method == "POST":
        email = request.POST['email'].strip().lower()
        password = request.POST['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            messages.error(request, "Invalid Email")
            return redirect('login')

        # check password
        if not check_password(password, user.password):
            messages.error(request, "Invalid Password")
            return redirect('login')

        # check email verified
        if not user.is_verified:
            messages.error(request, "Email not verified!")
            return redirect('login')

        # session login
        request.session['user_id'] = user.id

        messages.success(request, "Login Successful!")
        return redirect('index')

    return render(request, 'login.html')


#VERIFY EMAIL
def verify_email(request):
    token = request.GET.get('token')

    verification = EmailVerification.objects.filter(token=token).first()

    if not verification:
        messages.error(request, "Invalid or Expired Token")
        return redirect('register')

    user = verification.user
    user.is_verified = True
    user.save()

    verification.delete()

    messages.success(request, "Email Verified! Now login")
    return redirect('login')


#LOGOUT
def logout_view(request):
    request.session.flush()
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')


# FORGOT PASSWORD
def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email'].strip().lower()

        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(request, "Email not found!")
            return redirect('forgot_password')

        token = str(uuid.uuid4())

        PasswordReset.objects.create(
            user=user,
            token=token
        )

        print("Reset Link: http://127.0.0.1:8000/reset-password/?token=" + token)

        messages.success(request, "Check console for reset link!")
        return redirect('login')

    return render(request, 'forgot_password.html')


# RESET PASSWORD
def reset_password(request):
    token = request.GET.get('token')

    reset = PasswordReset.objects.filter(token=token).first()

    if not reset:
        messages.error(request, "Invalid or expired link")
        return redirect('login')

    if request.method == "POST":
        new_password = request.POST['password']

        user = reset.user
        user.password = make_password(new_password)
        user.save()

        reset.delete()

        messages.success(request, "Password updated successfully!")
        return redirect('login')

    return render(request, 'reset_password.html')