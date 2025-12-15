from .models import MenuItem
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from coffee.forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout

def home(request):
    return render(request, 'home.html')

def menu(request):
    category = request.GET.get('category')
    sort = request.GET.get('sort', '-created_at')

    items = MenuItem.objects.filter(in_stock=True)

    if category:
        items = items.filter(category=category)

    # Безопасная сортировка
    valid_sorts = ['-created_at', 'name', '-name', 'price', '-price']
    if sort in valid_sorts:
        items = items.order_by(sort)

    # Группировка (как раньше) — но теперь из отфильтрованных
    menu_dict = {}
    for item in items:
        cat_name = item.get_category_display()
        menu_dict.setdefault(cat_name, []).append(item)

    categories = [
        ('drink', 'Напитки'),
        ('dessert', 'Десерты'),
        ('snack', 'Закуски'),
    ]

    return render(request, 'menu.html', {
        'menu_items': menu_dict,
        'categories': categories,
        'current_category': category,
        'current_sort': sort,
    })

def menu_detail(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, in_stock=True)
    return render(request, 'menu_detail.html', {'item': item})

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
    
def custom_logout(request):
    logout(request)
    return redirect('home')
