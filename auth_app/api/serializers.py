from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration.

    Handles validation, user creation, and token generation.
    Ensures unique email addresses and matching passwords.
    """
    fullname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """Ensure email address is not already registered."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate(self, attrs):
        """Check if password and repeated_password match."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        """Create a new user after successful validation."""
        fullname = validated_data['fullname'].strip()
        first_name, last_name = self.split_fullname(fullname)
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=first_name,
            last_name=last_name,
            password=validated_data['password']
        )
        return user

    def split_fullname(self, fullname):
        """Split a full name into first and last name parts."""
        parts = fullname.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        return first_name, last_name

    def to_representation(self, instance):
        """Return a serialized representation including JWT token."""
        refresh = RefreshToken.for_user(instance)
        return {
            "token": str(refresh.access_token),
            "user_id": instance.id,
            "email": instance.email,
            "fullname": f"{instance.first_name} {instance.last_name}"
        }

class CustomTokenObtainPairSerializer(serializers.Serializer):
    """
    Serializer for user authentication (login).

    Authenticates a user via email and password, returning a JWT token
    and basic user details.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    fullname = serializers.CharField(read_only=True)

    def validate(self, attrs):
        """Authenticate the user and return JWT if successful."""
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("No active account found with the given credentials")

        refresh = RefreshToken.for_user(user)
        return {
            "token": str(refresh.access_token),
            "user_id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name} {user.last_name}"
        }