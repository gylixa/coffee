from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html

#Попытка удалить Theme (без ошибки, если не установлен)
try:
    from admin_interface.models import Theme
    admin.site.unregister(Theme)
except:
    pass

admin.site.unregister(Group)

#Импорт моделей
from .models import CustomUser, MenuItem, Order, OrderItem, Category

#Заголовок админки 
admin.site.site_header = "Админка «НЕ ФИЛЬТР»"
admin.site.site_title = "НЕ ФИЛЬТР"
admin.site.index_title = "Управление кофейней"

#Кастомный пользователь 
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'name', 'surname', 'patronymic', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'name', 'surname')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личные данные', {'fields': ('name', 'surname', 'patronymic', 'email')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'name', 'surname', 'patronymic', 'password1', 'password2'),
        }),
    )

#Категории 
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_count')
    search_fields = ('name',)
    
    def item_count(self, obj):
        return obj.menuitem_set.count()
    item_count.short_description = "Товаров"

#Меню (товары)
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'in_stock', 'stock', 'volume_ml', 'calories', 'is_vegan_icon')
    list_filter = ('category', 'in_stock', 'is_vegan')
    search_fields = ('name', 'description')
    list_editable = ('price', 'in_stock', 'stock')
    list_per_page = 20

    @admin.display(description="🌱", boolean=True)
    def is_vegan_icon(self, obj):
        return obj.is_vegan

#Позиции заказа
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('menu_item', 'quantity', 'price_per_unit', 'total_display')
    readonly_fields = ('total_display',)
    
    def total_display(self, obj):
        return f"{obj.quantity * obj.price_per_unit} ₽"
    total_display.short_description = "Итого"

#Заказы 
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_fio', 'status_badge', 'item_count', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('client__username', 'client__name', 'client__surname')
    readonly_fields = ('created_at', 'cancellation_reason_display')
    inlines = [OrderItemInline]
    
    def client_fio(self, obj):
        if obj.client:
            return f"{obj.client.surname} {obj.client.name}"
        return "Гость"
    client_fio.short_description = "Клиент"

    def status_badge(self, obj):
        colors = {
            'new': '#FFD700',
            'pending': '#17a2b8',
            'ready': '#28a745',
            'completed': '#20c997',
            'cancelled': '#dc3545',
        }
        display = obj.get_status_display()
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{}; color:white; padding:4px 8px; border-radius:4px; font-weight:bold;">{}</span>',
            color, display
        )
    status_badge.short_description = "Статус"

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Товаров"

    def cancellation_reason_display(self, obj):
        if obj.cancellation_reason:
            return format_html(
                '<div style="background:#f8d7da; color:#721c24; padding:10px; border-radius:4px; margin-top:10px;">'
                '<strong>Причина отмены:</strong> {}</div>',
                obj.cancellation_reason
            )
        return "-"
    cancellation_reason_display.short_description = "Причина отмены"

# Позиции заказа (отдельно)
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_link', 'menu_item_name', 'quantity', 'price_per_unit', 'total')
    list_filter = ('order__status',)  # фильтр по статусу заказа
    search_fields = ('order__id', 'menu_item__name')  # поиск по ID заказа или названию товара
    list_per_page = 20
    
    #Ссылка на заказ
    def order_link(self, obj):
        url = reverse('admin:main_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">Заказ #{}<a>', url, obj.order.id)
    order_link.short_description = "Заказ"
    
    #Название товара (чтобы не было menu_item.object)
    def menu_item_name(self, obj):
        return obj.menu_item.name if obj.menu_item else "Товар удалён"
    menu_item_name.short_description = "Menu Item"
    
    #Итого
    def total(self, obj):
        return f"{obj.quantity * obj.price_per_unit} ₽"
    total.short_description = "Итого"