from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from  rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from Library.settings import JWT_SECRET_KEY
from .serializers import UserSerializer
from .models import User
from utils.encryption import generate_token, decode_token
# Create your views here.


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['name', 'email', 'password']
    ),
    responses={
        201: 'Created',
        400: 'Bad Request',
    }
)
@api_view(["POST"])
def register_user(request):
    try:
        email = request.data.get('email')

        existing_user = User.objects.filter(email=email).exists()
        if existing_user:
            return Response({"status": False, "error": "User already exists"}, status=status.HTTP_409_CONFLICT)
        
        user = UserSerializer(data=request.data)
        user.is_valid(raise_exception=True)
        user.save()

        return Response({"status": True, "data": user.data}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"status": False, "data": "Internal Server Error" + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=[ 'email', 'password']
    ),
    responses={
        200: 'Ok',
        400: 'Bad Request',
    }
)
@api_view(["POST"])
def login_user(request):

    email = request.data.get("email")
    password = request.data.get("password")
    try:
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("user not found")
        
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect Password")
        
        token = generate_token(user)
        
        return Response({"status": True, "token": token}, status=status.HTTP_200_OK)
    
    except Exception:
        return Response({"status": True, "error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'auth-token',
            openapi.IN_HEADER,
            description="Token for authorization",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: 'Ok',
        400: 'Bad Request',
    }
)
@api_view(["GET"])
def get_user_profile(request):
    try:
        token = request.headers.get('auth-token')
        if not token:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        payload =  decode_token(token)

        if payload:
                return Response({"status":True, "data": payload}, status=status.HTTP_200_OK)
        else:
            return Response({"status":False, "error": payload}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception:
        return Response({"status":False, "error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
