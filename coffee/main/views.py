from .models import MenuItem, Order, OrderItem, Category
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from coffee.forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.http import JsonResponse
from coffee.cart import Cart
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

def menu(request):
    category_id = request.GET.get('category')
    sort = request.GET.get('sort', '-created_at')

    items = MenuItem.objects.filter(in_stock=True).select_related('category')

    if category_id and category_id.isdigit():
        items = items.filter(category_id=category_id)

    # 🔹 Безопасная сортировка: разрешаем новые поля
    valid_sorts = [
        '-created_at', 'name', '-name',
        'price', '-price',
        'volume_ml', '-volume_ml',
        'calories', '-calories',
        'is_vegan'  # False (0) → True (1): сначала веганские
    ]
    if sort in valid_sorts:
        items = items.order_by(sort)

    # Группировка по категориям
    menu_dict = {}
    for item in items:
        cat_name = item.category.name if item.category else "Без категории"
        menu_dict.setdefault(cat_name, []).append(item)

    categories = Category.objects.all()
    current_category_id = int(category_id) if category_id and category_id.isdigit() else None

    return render(request, 'menu.html', {
        'menu_items': menu_dict,
        'categories': categories,
        'current_category_id': current_category_id,
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

@login_required
def my_orders(request):
    orders = Order.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})

# Корзина
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})

def cart_add(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(MenuItem, id=item_id, in_stock=True)
    cart.add(item_id)
    
    # Показываем сообщение
    messages.success(request, f"«{item.name}» добавлен в корзину!")
    
    # Редирект туда, откуда пришёл (или в корзину)
    next_url = request.GET.get('next') or 'cart_detail'
    return redirect(next_url)

# Удалить
@require_POST
def cart_remove(request, item_id):
    cart = Cart(request)
    cart.remove(item_id)
    return redirect('cart_detail')

# Изменить кол-во
@require_POST
def cart_update(request):
    cart = Cart(request)
    item_id = request.POST.get('item_id')
    action = request.POST.get('action')

    item = get_object_or_404(MenuItem, id=item_id, in_stock=True)
    qty_in_cart = cart.cart.get(str(item_id), {}).get('quantity', 0)

    if action == 'inc':
        if qty_in_cart + 1 <= item.stock:
            cart.increment(item_id)
    elif action == 'dec':
        cart.decrement(item_id)

    return redirect('cart_detail')

# Оформление заказа 
@login_required
def order_create(request):
    cart = Cart(request)
    if not cart:
        return redirect('menu')

    if request.method == "POST":
        password = request.POST.get('password')
        if request.user.check_password(password):
            try:
                # Создаём заказ
                order = Order.objects.create(
                    client=request.user,
                    total=cart.get_total_price(),
                    status='new'
                )
                # Позиции
                for item_data in cart:
                    OrderItem.objects.create(
                        order=order,
                        menu_item=item_data['item'],
                        quantity=item_data['quantity'],
                        price_per_unit=item_data['item'].price
                    )
                cart.clear()
                return JsonResponse({
                    'success': True,
                    'message': 'Заказ оформлен! Бариста уже готовит ☕',
                    'redirect_url': '/'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': 'Ошибка при создании заказа. Попробуйте позже.'
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Неверный пароль. Попробуйте снова.'
            })

    return render(request, 'order_create.html', {'cart': cart})

@login_required
def profile(request):
    # Заказы пользователя, новые — сверху
    orders = Order.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'orders': orders})

# Удаление заказа (только новых)
@require_POST
@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, client=request.user)
    if order.status == 'new':
        order.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Можно удалять только новые заказы.'}, status=400)
