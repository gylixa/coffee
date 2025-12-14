from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import re

# Кастомная модель пользователя
class CustomUser(AbstractUser):
    # Валидатор для логина - только латиница и цифры, минимум 6 символов
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9]{6,}$',
        message='Логин должен содержать только латинские буквы и цифры, минимум 6 символов'
    )

    # Валидатор для ФИО - только кириллица и пробелы
    fio_validator = RegexValidator(
        regex=r'^[а-яА-ЯёЁ\s]+$',
        message='ФИО должно содержать только кириллические символы и пробелы'
    )

    # Валидатор для телефона - строгий формат 8(XXX)XXX-XX-XX
    phone_validator = RegexValidator(
        regex=r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$',
        message='Телефон должен быть в формате: 8(XXX)XXX-XX-XX'
    )

    # Поле логина с валидацией и уникальностью
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Логин',
        error_messages={
            'unique': "Пользователь с таким логином уже существует.",
        },
    )
    # Поле ФИО с валидацией кириллицы
    fio = models.CharField(
        max_length=255,
        validators=[fio_validator],
        verbose_name='ФИО'
    )
    # Поле телефона с валидацией формата
    phone = models.CharField(
        max_length=15,
        validators=[phone_validator],
        verbose_name='Телефон'
    )
    # Поле email с уникальностью
    email = models.EmailField(unique=True, verbose_name='Email')

    # Отключение стандартных полей имени и фамилии
    first_name = None
    last_name = None

    # Поля, обязательные при создании суперпользователя
    REQUIRED_FIELDS = ['email', 'fio', 'phone']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    # Строковое представление пользователя
    def __str__(self):
        return f"{self.fio} ({self.username})"
    
class MenuItem(models.Model):  # ← "Меню" из диаграммы → переименовал, чтобы не путать с HTML-меню
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
