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

# Create your views here.

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

    def get_serializer_class(self):
        from .serializers import CustomTokenObtainPairSerializer
        return CustomTokenObtainPairSerializer

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
