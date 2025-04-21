from rest_framework import serializers
from .models import User, UserRole
from rest_framework.serializers import  ModelSerializer, Serializer,SerializerMethodField
from rest_framework.fields import  CharField, EmailField
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.exceptions import ValidationError
from django.db.transaction import atomic
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterSerializer(ModelSerializer):
    password = CharField(write_only=True)
    first_name = CharField(required=False)

    class Meta:
        model = User
        fields = ("first_name", "email", "password","username")
        
    @atomic
    def create(self, validated_data):
        try:
            # Check if the optional fields are present in validated_data
            first_name = validated_data.get("first_name")
            username = validated_data.get("username")

            user = User.objects.create_user(
                username=validated_data["username"].lower(),
                email=validated_data["email"].lower(),
                first_name=username,
                password=validated_data["password"],
            )
            return user
        
        except Exception as e:
            error_message = {"error": "Something went wrong!"}
            status_code = HTTP_500_INTERNAL_SERVER_ERROR

            if e.args:
                error_message = {
                    "error": e
                }
                status_code = HTTP_400_BAD_REQUEST

            raise ValidationError(error_message, status_code)
        
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': getattr(user.user_role, 'role_name', None),}


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__' 
        
class UserSerializer(serializers.ModelSerializer):
    role = UserRoleSerializer(read_only=True)
    user_role = serializers.PrimaryKeyRelatedField(queryset=UserRole.objects.all(), write_only=True)
    user_role_details = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_role', 'first_name', 'last_name', 'is_active', 'is_staff', 'role','user_role_details']

    
    
    def create(self, validated_data):
        user_role = validated_data.pop('user_role')
        
        # Extract username & email
        username = validated_data.get('username')
        email = validated_data.get('email')
        # Default password
        password = "User@123"

        # Permission flags
        is_staff = False
        is_superuser = False

        if user_role.role_name == 'SuperAdmin':
            is_staff = True
            is_superuser = True
        elif user_role.role_name == 'Admin':
            is_staff = True

        # Create user with proper method
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        user.user_role = user_role
        user.save()
        return user

    def update(self, instance, validated_data):
        user_role = validated_data.pop('user_role', None)
        if user_role:
            instance.user_role = user_role
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


    def get_user_role_details(self, obj):
        if obj.user_role:
            return {
                "id": obj.user_role.id,
                "role_name": obj.user_role.role_name,
                "role_code": obj.user_role.role_code,
                "title": obj.user_role.title,
                "description": obj.user_role.description
            }
        return None
