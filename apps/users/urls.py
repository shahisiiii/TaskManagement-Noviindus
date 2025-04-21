from django.urls import include, path
from .views import CustomTokenObtainPairView, RegisterUserView, UserAuthView, UserProfileView, UserViewSet
from rest_framework.routers import DefaultRouter
from .views import UserRoleViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'user-roles', UserRoleViewSet)
router.register(r'login', UserAuthView, basename='user-login')

urlpatterns = [
    path(r"register/", RegisterUserView.as_view(), name="register"),
    path(r'login/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    
] 