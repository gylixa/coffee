from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

try:
    from admin_interface.models import Theme
    admin.site.unregister(Theme)
except:
    pass

admin.site.unregister(Group)

# Импорт моделей
from .models import CustomUser, MenuItem, Order, OrderItem, Category

#Кастомный пользователь 
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'name', 'surname', 'is_staff')
    search_fields = ('username', 'email', 'name', 'surname')
    ordering = ('-date_joined',)

#  Меню (товары) 
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'in_stock')
    list_filter = ('category', 'in_stock') 
    search_fields = ('name',)
    list_editable = ('price', 'in_stock')  

# Заказы 
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_fio', 'status', 'item_count', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('client__username', 'client__name', 'client__surname')
    readonly_fields = ('created_at',)
    
    # ФИО заказчика
    def client_fio(self, obj):
        if obj.client:
            return f"{obj.client.surname} {obj.client.name}"
        return "Гость"
    client_fio.short_description = "ФИО заказчика"
    client_fio.admin_order_field = 'client__surname'

    # Количество товаров
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Товаров"

#  Позиции заказа (для полноты) 
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'price_per_unit')
    list_filter = ('order__status',)

admin.site.register(Category)