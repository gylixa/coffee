# cafe/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser, MenuItem, Order, OrderItem

# Удаляем Theme из admin-interface (если установлен)
try:
    from admin_interface.models import Theme
    admin.site.unregister(Theme)
except:
    pass  # Если пакет не установлен — игнорируем

# Удаляем Group — как в твоём примере
admin.site.unregister(Group)


# ─── Регистрация моделей ──────────────────────────────

# Кастомный пользователь
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'name', 'surname', 'is_staff')
    search_fields = ('username', 'email', 'name', 'surname')
    ordering = ('-date_joined',)

# Меню
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'in_stock')
    list_filter = ('category', 'in_stock')
    search_fields = ('name',)

# Заказы и позиции
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('client__username', 'client__name')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at',)