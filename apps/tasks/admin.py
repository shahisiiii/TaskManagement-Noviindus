from django.contrib import admin

from apps.users.models import UserRole
from .models import Task

# Register your models here.
from django.contrib import admin
from .models import User, Task
from django.contrib.auth.models import Group

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'status', 'due_date', 'completion_report')
    list_filter = ('status', 'assigned_to')
    search_fields = ('title', 'description')

    # Show or hide actions based on the user's role
    def get_queryset(self, request):
        if request.user.user_role and request.user.user_role.role_name == 'SuperAdmin':
            return Task.objects.all()  # SuperAdmins can see all tasks
        elif request.user.user_role and request.user.user_role.role_name == 'Admin':
            return Task.objects.filter(assigned_to=request.user)  # Admins can only see tasks assigned to them
        return Task.objects.none()

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_role', 'is_active')
    list_filter = ('user_role', 'is_active')
    search_fields = ('username', 'email')

    # Restricting actions based on the user role
    def get_queryset(self, request):
        if request.user.user_role and request.user.user_role.role_name == 'SuperAdmin':
            return User.objects.all()  # SuperAdmins can see all users
        elif request.user.user_role and request.user.user_role.role_name == 'Admin':
            return User.objects.filter(user_role__name='User')  # Admins can only see users with the role 'User'
        return User.objects.none()

admin.site.register(Task, TaskAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserRole)
admin.site.unregister(Group)  # Unregister the default Group admin if you're using custom roles
