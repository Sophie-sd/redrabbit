"""
Форми для користувачів
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile


class WholesaleRegistrationForm(UserCreationForm):
    """Форма реєстрації для оптових клієнтів"""
    
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')
    first_name = forms.CharField(max_length=30, required=True, label="Ім'я")
    last_name = forms.CharField(max_length=30, required=True, label='Прізвище')
    company_name = forms.CharField(max_length=200, required=False, label='Назва компанії')
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'first_name', 'last_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Додаємо CSS класи для стилізації
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Створюємо профіль користувача
            UserProfile.objects.create(
                user=user,
                company_name=self.cleaned_data.get('company_name', '')
            )
        
        return user
