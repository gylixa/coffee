from .models import MenuItem
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login
from coffee.forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView

def home(request):
    return render(request, 'home.html')

def menu(request):
    items = MenuItem.objects.all().order_by('category', 'name')
    # Группируем по категориям
    menu_dict = {}
    for item in items:
        cat_display = dict(MenuItem.CATEGORY_CHOICES)[item.category]
        menu_dict.setdefault(cat_display, []).append(item)
    return render(request, 'menu.html', {'menu_items': menu_dict})

def contacts(request):
    return render(request, 'contacts.html')

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.name}! Ваш аккаунт создан. +100 бонусов уже на счету ☕")
            return redirect('home')
        else:
            pass
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        # Перехватываем ошибки и заменяем на русские
        for field in form.errors:
            for error in form.errors[field]:
                if "username" in error.lower() or "password" in error.lower():
                    messages.error(self.request, "Неверный логин или пароль.")
                elif "inactive" in error.lower():
                    messages.error(self.request, "Ваш аккаунт не активирован.")
                else:
                    messages.error(self.request, "Ошибка при входе. Проверьте данные.")
        return super().form_invalid(form)
