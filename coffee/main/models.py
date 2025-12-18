from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import re

class CustomUser(AbstractUser):
    # Валидаторы
    name_validator = RegexValidator(
        regex=r'^[а-яА-ЯёЁ\s\-]+$',
        message='Имя должно содержать только кириллицу, пробелы и тире.'
    )
    surname_validator = RegexValidator(
        regex=r'^[а-яА-ЯёЁ\s\-]+$',
        message='Фамилия должна содержать только кириллицу, пробелы и тире.'
    )
    patronymic_validator = RegexValidator(
        regex=r'^[а-яА-ЯёЁ\s\-]*$',
        message='Отчество должно содержать только кириллицу, пробелы и тире.'
    )
    login_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9\-]{3,30}$',
        message='Логин: латиница, цифры, тире; 3–30 символов.'
    )

    # Поля
    name = models.CharField('Имя', max_length=100, validators=[name_validator])
    surname = models.CharField('Фамилия', max_length=100, validators=[surname_validator])
    patronymic = models.CharField('Отчество', max_length=100, validators=[patronymic_validator], blank=True)
    
    username = models.CharField(
        'Логин',
        max_length=30,
        unique=True,
        validators=[login_validator],
        error_messages={'unique': 'Пользователь с таким логином уже существует.'}
    )
    
    email = models.EmailField('Email', unique=True)
    
    # Отключаем старые поля
    first_name = None
    last_name = None

    REQUIRED_FIELDS = ['email', 'name', 'surname']

    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic}".strip() or self.username
class Category(models.Model):
    name = models.CharField("Название", max_length=100, unique=True)

    def __str__(self):
            return self.name

    class Meta:
            verbose_name = "Категория"
            verbose_name_plural = "Категории"
            
class MenuItem(models.Model):

    name = models.CharField("Название", max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,  # нельзя удалить категорию, если есть товары
        verbose_name="Категория"
    )
    price = models.DecimalField("Цена", max_digits=6, decimal_places=2)
    description = models.TextField("Описание", blank=True)
    
    #когда добавили
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)
    
    # git add .в наличии ли?
    in_stock = models.BooleanField("В наличии", default=True)

    # фото
    image = models.ImageField("Фото", upload_to="menu/", blank=True, null=True)
    stock = models.PositiveIntegerField("Остаток", default=999)  # 999 = "много"
    volume_ml = models.PositiveSmallIntegerField("Объём, мл", blank=True, null=True)
    calories = models.PositiveSmallIntegerField("Калории, ккал", blank=True, null=True)
    is_vegan = models.BooleanField("Веганский", default=False, blank=True)
    # Метод: сколько можно добавить в корзину
    def max_addable(self, already_in_cart=0):
        if not self.in_stock:
            return 0
        return max(0, self.stock - already_in_cart)
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']  # новые — первыми
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),          
        ('pending', 'Принят'),
        ('ready', 'Готов'),
        ('completed', 'Выдан'),
        ('cancelled', 'Отменён'),
    ]
    client = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name="Клиент")
    created_at = models.DateTimeField("Дата и время", auto_now_add=True)
    total = models.DecimalField("Итого", max_digits=8, decimal_places=2, default=0)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='new')
    cancellation_reason = models.TextField("Причина отмены", blank=True)

    def __str__(self):
        return f"Заказ #{self.id} от {self.created_at.strftime('%d.%m %H:%M')}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("Количество", default=1)
    price_per_unit = models.DecimalField("Цена за шт.", max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}× {self.menu_item.name}"
