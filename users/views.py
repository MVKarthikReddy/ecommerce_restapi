from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import CustomUserSerializer

@api_view(['POST'])
def register(request):
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully!"})
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = CustomUser.objects.filter(email=email).first()
    if user and user.check_password(password):
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({"message": "Invalid credentials"}, status=400)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == 'GET':
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = CustomUserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
