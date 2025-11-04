# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'phone', 'password', 'password2')
        extra_kwargs = {
            'full_name': {'required': False},
            'phone': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn’t match."})
        return attrs

    def create(self, validated_data):
        # Remove password2 before user creation
        password = validated_data.pop('password')
        validated_data.pop('password2', None)

        # Handle optional fields safely
        full_name = validated_data.pop('full_name', '')
        phone = validated_data.pop('phone', '')

        # Create user instance
        user = User.objects.create(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
        )

        # Add optional fields if exist in model
        if hasattr(user, 'full_name'):
            user.full_name = full_name
        if hasattr(user, 'phone'):
            user.phone = phone

        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'full_name', 'phone')
