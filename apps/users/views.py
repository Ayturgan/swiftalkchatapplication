# views.py
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages  # Добавьте импорт
from .forms import UserRegisterForm, UserUpdateForm
from .models import CustomUser


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Получите международный формат номера из скрытого поля full_phone
            full_phone = form.cleaned_data['full_phone']

            user = CustomUser(
                username=form.cleaned_data['username'],
                full_phone=full_phone  # Используйте международный формат номера
            )
            user.set_password(form.cleaned_data['password1'])  # Установите хешированный пароль
            user.save()
            return redirect('login')
        else:
            messages.error(request, 'Registration failed. Please check the form for errors.')
    else:
        form = UserRegisterForm()
    return render(request, 'swiftalk/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'swiftalk/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def reset_password(request):
    return render(request, 'swiftalk/password-reset.html')


def get_user_data(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user_data = {
            'avatar': user.avatar.url,
        }
        return JsonResponse(user_data)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)


def update_profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('home')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'swiftalk/settings.html', {'form': form})


