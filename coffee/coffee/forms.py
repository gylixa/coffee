

from django import forms
from django.contrib.auth.forms import UserCreationForm
from main.models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=6,
        help_text='Не менее 8 символов.'
    )
    password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=6
    )
    rules = forms.BooleanField(
        label='Я согласен с правилами регистрации',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input me-2'}),
        error_messages={'required': 'Необходимо согласиться с правилами.'}
    )

    class Meta:
        model = CustomUser
        fields = ('name', 'surname', 'patronymic', 'username', 'email')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван'}),
            'surname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванович (необязательно)'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ivan_ivanov'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ivan@example.com'}),
        }
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'patronymic': 'Отчество',
            'username': 'Логин',
            'email': 'Email',
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data