from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import  status

from rest_framework.permissions import IsAuthenticated,AllowAny

from apps.users.permissions import IsSuperAdmin
from .serializers import RegisterSerializer, UserSerializer
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from apps.users.models import User, UserRole
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .models import UserRole
from .serializers import UserRoleSerializer
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response

# Create your views here.



from django.contrib import messages
from .forms import UserEditForm, UserForm

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework.status import HTTP_201_CREATED
from .serializers import RegisterSerializer
from rest_framework.exceptions import ValidationError
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from apps.users.models import User
from apps.tasks.models import Task

from apps.tasks.forms import TaskForm

class RegisterUserView(CreateAPIView):
    """
    User registration endpoint.
    """

    model = User
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def perform_create(self, serializer):
        user = serializer.save()

        try:
            default_role = UserRole.objects.get(role_code="SuperAdmin")  # or "SuperAdmin"
            user.user_role = default_role
            user.save()
        except UserRole.DoesNotExist:
            pass  # Optionally raise an error or log


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    
class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        request_data = request.data.copy()
        if 'username' in request_data:
            request_data['username'] = request_data['username'].lower()

        request._full_data = request_data

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            user = User.objects.get(username=request.data['username'])
            response.data['name'] = user.first_name
            response.data['email'] = user.email
            response.data['user_role'] = user.user_role.role_name

        return response


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer


User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        """
        Only SuperAdmin can create a user.
        """
        print('test role ',self.request.user.user_role.role_code)

        if self.request.user.user_role and self.request.user.user_role.role_code == 'SuperAdmin':
            serializer.save()
        else:
            raise PermissionDenied("You must be a SuperAdmin to create a user.")

    def perform_update(self, serializer):
        """
        Only SuperAdmin can update a user.
        """
        if self.request.user.user_role and self.request.user.user_role.role_code == 'SuperAdmin':
            serializer.save()
        else:
            raise PermissionDenied("You must be a SuperAdmin to update a user.")

    def perform_destroy(self, instance):
        """
        Only SuperAdmin can delete a user.
        """
        if self.request.user.user_role and self.request.user.user_role.role_code == 'SuperAdmin':
            instance.delete()
        else:
            raise PermissionDenied("You must be a SuperAdmin to delete a user.")
        
    @action(detail=False, methods=['get'], url_path='only-users')
    def list_only_users(self, request):
        """
        Custom action to list all users where user_role.role_code == 'User'
        """
        user_role_code = 'User'
        users = User.objects.filter(user_role__role_code=user_role_code)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
class UserAuthView(viewsets.ViewSet):
    queryset = User.objects.all()

    def get_permissions(self):
        print(self.action)
        if self.action in ['mobile_login']: 
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'], url_path='mobile-login')
    def mobile_login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Phone number and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({"error": "Invalid Password."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({"error": "User account is not active."}, status=status.HTTP_403_FORBIDDEN)
        

        user_tokens = user.get_tokens()
        return Response(
        {
            "refresh": user_tokens["refresh"],
            "access": user_tokens["access"],
            "name": None,
            "email": user.email,
        }
    )








def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password']) 
            user.save()
            login(request, user)  
            return redirect('dashboard')  
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')




@login_required
def dashboard_view(request):
    user = request.user
    context = {}

    if user.user_role.role_name == 'SuperAdmin':
        context['users'] = User.objects.exclude(id=user.id)
        context['admins'] = User.objects.filter(user_role__role_name='Admin')
        context['tasks'] = Task.objects.all()
        context['reports'] = Task.objects.filter(status='Completed')

    elif user.user_role.role_name == 'Admin':
        context['tasks'] = Task.objects.filter(assigned_by=user)
        context['reports'] = Task.objects.filter(assigned_by=user,status='Completed')

    elif user.user_role.role_name == 'User':
        context['tasks'] = Task.objects.filter(assigned_to=user)
        context['reports'] = Task.objects.filter(assigned_to=user,status='Completed')

    return render(request, 'users/dashboard.html', context)

  # Ensure this is the correct form for your custom User model

@login_required
def create_user(request):
    if request.user.user_role.role_name != 'SuperAdmin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully!')
            return redirect('dashboard')
        else:
            print(form.errors)

            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserForm()

    return render(request, 'users/create_user.html', {'form': form})

@login_required
def delete_user(request, user_id):
    # Ensure that the user has permission to delete
    if request.user.user_role.role_name != 'SuperAdmin':
        messages.error(request, "You don't have permission to delete users.")
        return redirect('dashboard')

    user_to_delete = get_object_or_404(User, id=user_id)
    
    # Deleting the user
    user_to_delete.delete()
    
    messages.success(request, 'User deleted successfully!')
    return redirect('dashboard')




@login_required
def create_task(request):
    if not request.user.user_role.role_name in ['Admin','SuperAdmin']:
        return redirect('dashboard')

    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            return redirect('dashboard')
    else:
        form = TaskForm(user=request.user)

    return render(request, 'users/create_task.html', {'form': form})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('dashboard')  # adjust to your actual task list view name


def register_template_view(request):
    if request.method == "POST":
        data = {
            "username": request.POST.get("username"),
            "first_name": request.POST.get("first_name"),
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
        }

        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()

            # Assign default user role
            try:
                default_role = UserRole.objects.get(role_code="SuperAdmin")  # Change as needed
                user.user_role = default_role
                user.save()
            except UserRole.DoesNotExist:
                messages.error(request, "Default role does not exist.")

            messages.success(request, "Account created successfully!")
            return redirect("login")  # Change as needed
        else:
            return render(request, "users/register.html", {"form": serializer})
    
    return render(request, "users/register.html", {"form": {}})


@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Replace with your actual redirect
    else:
        form = UserEditForm(instance=user)

    return render(request, 'users/edit_user.html', {'form': form})


def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # or wherever you want to redirect
    else:
        form = TaskForm(instance=task)
    return render(request, 'users/edit_task.html', {'form': form})
