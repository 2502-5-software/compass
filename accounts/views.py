from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib import messages
from django.views import View
from django.contrib.auth import login
from django.contrib.auth import authenticate, logout
from .serializers import RegisterSerializer, UserSerializer, RoleUpdateSerializer, LoginSerializer, ProfileDetailSerializer
from rest_framework import generics, permissions, status
from .models import CustomUser, Profile
from .permissions import IsSuperAdmin
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
class RegisterView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'accounts/register.html', {'user_form': form})
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
        return render(request, 'accounts/register.html', {'user_form': form})

class LoginView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'accounts/login.html', {'login_form': form})
    
    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful.')
                return redirect('index')
            else:
                messages.error(request, 'Invalid email or password.')
        return render(request, 'accounts/login.html', {'login_form': form})
    
class logoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('login')
    
    
class RegisterAPIView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
class UserListAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    
class AssignRoleAPIView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RoleUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    lookup_field = 'pk'
    
class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"