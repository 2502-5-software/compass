from django.urls import path
from .views import RegisterView, LoginView, logoutView, RegisterAPIView, AssignRoleAPIView, UserListAPIView, LoginAPIView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logoutView.as_view(), name='logout'),
    path('api/register/', RegisterAPIView.as_view(), name='register'),
    path('api/users/', UserListAPIView.as_view(), name='users'),
    path('api/users/<int:pk>/assign-role/', AssignRoleAPIView.as_view(), name='assign-role'),
    path("api/login/", LoginAPIView.as_view(), name='login'),
    
    
]

