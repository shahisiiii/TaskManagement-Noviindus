from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['username']
    user_role = models.ForeignKey('users.UserRole',on_delete=models.SET_NULL,blank=True,null=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
class UserRole(models.Model):
    role_name = models.CharField(max_length=255,unique=True)
    role_code = models.CharField(max_length=255)
    title = models.CharField(max_length=225, null=True,blank=True)
    description = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.role_name