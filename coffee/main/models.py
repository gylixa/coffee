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
    
class MenuItem(models.Model): 
    CATEGORY_CHOICES = [
        ('drink', 'Напиток'),
        ('dessert', 'Десерт'),
        ('snack', 'Закуска'),
    ]
    name = models.CharField("Название", max_length=100)
    category = models.CharField("Категория", max_length=20, choices=CATEGORY_CHOICES, default='drink')
    price = models.DecimalField("Цена", max_digits=6, decimal_places=2)
    description = models.TextField("Описание", blank=True)

    def __str__(self):
        return self.name
    
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

    def __str__(self):
        return f"Заказ #{self.id} от {self.created_at.strftime('%d.%m %H:%M')}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("Количество", default=1)
    price_per_unit = models.DecimalField("Цена за шт.", max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}× {self.menu_item.name}"
