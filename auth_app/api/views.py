from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model

from .serializers import RegistrationSerializer

User = get_user_model()

class RegistrationView(APIView):
    """
    API endpoint for user registration.

    Creates a new user account and returns an authentication token.
    Accessible without authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new user."""
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            data = serializer.to_representation(user)
            data["token"] = token.key
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(APIView):
    """
    API endpoint for user login.

    Authenticates user credentials and returns an authentication token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Login with email and password, return token and user info."""
        email, password = request.data.get("email"), request.data.get("password")
        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=400)

        user = authenticate(username=email, password=password)
        if not user:
            return Response({"detail": "Invalid credentials."}, status=400)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key, "user_id": user.id,
            "email": user.email, "fullname": f"{user.first_name} {user.last_name}"
        }, status=200)
    
class EmailCheckView(APIView):
    """
    API endpoint for verifying if an email exists in the system.

    Used for frontend validation when adding collaborators or new users.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """Check if a user with the given email exists."""
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