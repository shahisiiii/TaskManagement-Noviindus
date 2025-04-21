from django import forms
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        if user and hasattr(user, 'user_role') and user.user_role.role_name == 'Admin':
            self.fields['assigned_to'].queryset = User.objects.filter(assigned_admin=user).exclude(id=user.id,user_role__role_name='User')
        if user and hasattr(user, 'user_role') and user.user_role.role_name == 'SuperAdmin':
            self.fields['assigned_to'].queryset = User.objects.exclude(
                id=user.id
            ).filter(
                user_role__role_name='User'
            )
