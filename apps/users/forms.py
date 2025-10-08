"""
Форми для користувачів
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, UserProfile
import re


class WholesaleRegistrationForm(UserCreationForm):
    """Форма реєстрації для оптових клієнтів"""
    
    email = forms.EmailField(
        required=True, 
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'example@email.com',
            'autocomplete': 'email'
        })
    )
    phone = forms.CharField(
        max_length=13, 
        required=True, 
        label='Телефон',
        widget=forms.TextInput(attrs={
            'placeholder': '+380991234567',
            'pattern': r'\+380\d{9}',
            'autocomplete': 'tel'
        }),
        help_text='Формат: +380XXXXXXXXX'
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        label="Ім'я",
        widget=forms.TextInput(attrs={
            'placeholder': "Ім'я",
            'autocomplete': 'given-name'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        label='Прізвище',
        widget=forms.TextInput(attrs={
            'placeholder': 'Прізвище',
            'autocomplete': 'family-name'
        })
    )
    date_of_birth = forms.DateField(
        required=True,
        label='Дата народження',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'placeholder': 'ДД.ММ.РРРР'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'date_of_birth', 'phone', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Додаємо CSS класи для стилізації
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
            })
    
    def clean_phone(self):
        """Валідація телефону"""
        phone = self.cleaned_data.get('phone')
        
        # Перевірка формату
        if not re.match(r'^\+380\d{9}$', phone):
            raise ValidationError(
                'Невірний формат телефону. Використовуйте формат +380XXXXXXXXX'
            )
        
        # Перевірка унікальності
        if CustomUser.objects.filter(phone=phone).exists():
            raise ValidationError('Цей номер телефону вже зареєстрований')
        
        return phone
    
    def clean_email(self):
        """Валідація email"""
        email = self.cleaned_data.get('email')
        
        # Перевірка унікальності
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Ця email адреса вже зареєстрована')
        
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        
        # Генеруємо username з email якщо не вказано
        if not user.username:
            user.username = self.cleaned_data['email'].split('@')[0]
        
        # Користувач неактивний до підтвердження email
        user.is_active = False
        user.is_wholesale = False
        
        if commit:
            user.save()
            
            # Створюємо профіль користувача
            UserProfile.objects.get_or_create(user=user)
        
        return user
