"""
Форми для користувачів
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
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
        required=False, 
        label='Телефон (необов\'язково)',
        widget=forms.TextInput(attrs={
            'placeholder': '+380991234567',
            'pattern': r'\+380\d{9}',
            'autocomplete': 'tel'
        }),
        help_text='Формат: +380XXXXXXXXX'
    )
    first_name = forms.CharField(
        max_length=100, 
        required=True, 
        label="Повне ім'я",
        widget=forms.TextInput(attrs={
            'placeholder': "Ваше повне ім'я",
            'autocomplete': 'name'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'phone', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Додаємо CSS класи для стилізації
        for field_name, field in self.fields.items():
            if field_name in ['password1', 'password2']:
                field.widget.attrs.update({
                    'class': 'form-control password-field',
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-control',
                })
    
    def clean_phone(self):
        """Валідація телефону"""
        phone = self.cleaned_data.get('phone')
        
        # Якщо телефон не вказано, повертаємо порожнє значення
        if not phone:
            return ''
        
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
        user.phone = self.cleaned_data.get('phone', '')
        user.first_name = self.cleaned_data['first_name']
        user.last_name = ''
        
        # Генеруємо унікальний username з email
        if not user.username:
            base_username = self.cleaned_data['email'].split('@')[0]
            username = base_username
            counter = 1
            
            # Перевіряємо унікальність username
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user.username = username
        
        # Користувач неактивний до підтвердження email
        user.is_active = False
        # Оптовий статус за замовчуванням True - буде активовано після підтвердження email
        user.is_wholesale = True
        
        if commit:
            user.save()
            
            # Створюємо профіль користувача
            UserProfile.objects.get_or_create(user=user)
        
        return user


class CustomLoginForm(AuthenticationForm):
    """Покращена форма входу з валідацією"""
    
    username = forms.CharField(
        label='Email або номер телефону',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com або +380991234567',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control password-field',
            'placeholder': '••••••••',
            'autocomplete': 'current-password'
        })
    )


class CustomPasswordResetForm(PasswordResetForm):
    """Покращена форма відновлення паролю"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'example@email.com',
            'autocomplete': 'email'
        })
    
    def get_users(self, email):
        """Повертає користувачів з вказаним email"""
        active_users = CustomUser._default_manager.filter(
            email__iexact=email,
            is_active=True
        )
        return (
            user for user in active_users
            if user.has_usable_password()
        )


class ProfileEditForm(forms.ModelForm):
    """Форма редагування профілю користувача"""
    
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label="Повне ім'я",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Ваше повне ім'я",
            'autocomplete': 'name'
        })
    )
    
    phone = forms.CharField(
        max_length=13,
        required=True,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+380991234567',
            'pattern': r'\+380\d{9}',
            'autocomplete': 'tel'
        }),
        help_text='Формат: +380XXXXXXXXX'
    )
    
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com',
            'autocomplete': 'email',
            'readonly': 'readonly'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'phone', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True
    
    def clean_phone(self):
        """Валідація телефону"""
        phone = self.cleaned_data.get('phone')
        
        if not re.match(r'^\+380\d{9}$', phone):
            raise ValidationError(
                'Невірний формат телефону. Використовуйте формат +380XXXXXXXXX'
            )
        
        # Перевірка унікальності (виключаючи поточного користувача)
        if CustomUser.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Цей номер телефону вже зареєстрований')
        
        return phone
