from django import forms
from apps.users.models import User, UserRole  
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")


class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_role = forms.ModelChoiceField(
        queryset=UserRole.objects.all(),
        empty_label="Select a role",
        required=True,
        label="Role"
    )
    assigned_admin = forms.ModelChoiceField(
        queryset=User.objects.filter(user_role__role_name='Admin'),
        empty_label="Select a Admin",
        required=False,
        label="AssignedAdmin"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_role','assigned_admin']


class UserEditForm(forms.ModelForm):
    user_role = forms.ModelChoiceField(queryset=UserRole.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'user_role']
