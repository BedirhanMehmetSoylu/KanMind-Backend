from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializer
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            data = serializer.to_representation(user)
            data["token"] = token.key
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(username=email, password=password)
        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name} {user.last_name}"
        })
    
class EmailCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response(
                {"detail": "Email parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"exists": False}, status=status.HTTP_200_OK)

        return Response({
            "exists": True,
            "id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name} {user.last_name}"
        }, status=status.HTTP_200_OK)