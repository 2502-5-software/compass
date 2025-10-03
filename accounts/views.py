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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

auth_header = openapi.Parameter(
    "Authorization",
    openapi.IN_HEADER,
    description="JWT access token. Format: Bearer <token>",
    type=openapi.TYPE_STRING,
    required=True
)
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
    
    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=RegisterSerializer,
        responses={201: RegisterSerializer()},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    
class UserListAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    
    @swagger_auto_schema(
        operation_description="Retrieve a list of all users (SuperAdmin only)",
        manual_parameters=[auth_header],
        responses={200: UserSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class AssignRoleAPIView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RoleUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    lookup_field = 'pk'
    
    @swagger_auto_schema(
        operation_description="Assign or change a user's role (SuperAdmin only)",
        manual_parameters=[auth_header],
        request_body=RoleUpdateSerializer,
        responses={200: RoleUpdateSerializer()},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
class LoginAPIView(APIView):
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="User password"),
            },
            required=["email", "password"],
        ),
        responses={
            200: openapi.Response(
                description="Login success",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "email": "john@example.com",
                            "username": "john_doe",
                            "role": "Admin"
                        },
                        "refresh": "your-refresh-token",
                        "access": "your-access-token"
                    }
                },
            ),
            400: "Invalid credentials",
        }
    ) 
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
    
    @swagger_auto_schema(
        operation_description="Retrieve or update user profile",
        manual_parameters=[auth_header],
        responses={200: ProfileDetailSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)