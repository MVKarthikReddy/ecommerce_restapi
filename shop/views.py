from django.shortcuts import render

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import User

# User Registration
@api_view(['POST'])
def register(request):
    email = request.data['email']
    password = request.data['password']
    user = User.objects.create_user(username=email, email=email, password=password)
    return Response({"message": "User created successfully!"})

# JWT Token generation
@api_view(['POST'])
def login(request):
    email = request.data['email']
    password = request.data['password']
    user = User.objects.filter(email=email).first()
    if user and user.check_password(password):
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({"message": "Invalid credentials"}, status=400)

# Profile Management
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == 'GET':
        return Response({
            'name': request.user.username,
            'email': request.user.email,
        })
    elif request.method == 'PUT':
        request.user.username = request.data.get('name', request.user.username)
        request.user.save()
        return Response({"message": "Profile updated"})

