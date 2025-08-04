from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your email address'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Choose a username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm your password'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter your username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter your password'
        })

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter your current password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter your new password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm your new password'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        
        if old_password and new_password1:
            if old_password == new_password1:
                raise forms.ValidationError(
                    "Your new password must be different from your current password."
                )
        
        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar', 'birth_date', 'location', 'favorite_genres']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'maxlength': 500,
                'placeholder': 'Tell us about yourself and your movie preferences...'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your location'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            }),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your email address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your last name'
            }),
        }