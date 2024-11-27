import re
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User
from rest_framework.validators import UniqueValidator


def validate_username(value):
    """
    Validate that the username contains only letters and numbers.
    """
    if not re.match(r'^[a-zA-Z0-9]+$', value):
        raise serializers.ValidationError(
            "Username must only contain letters and numbers."
        )
    return value


def validate_password(value):
    """
    Validate that the password is at least 6 characters long
    and contains at least 1 lowercase letter, 1 uppercase letter,
    1 digit, and 1 special character.
    """
    if len(value) < 6:
        raise serializers.ValidationError(
            "Password must be at least 6 characters long.")

    if not re.search(r'[a-z]', value):
        raise serializers.ValidationError(
            "Password must contain at least 1 lowercase letter.")

    if not re.search(r'[A-Z]', value):
        raise serializers.ValidationError(
            "Password must contain at least 1 uppercase letter.")

    if not re.search(r'[0-9]', value):
        raise serializers.ValidationError(
            "Password must contain at least 1 number.")

    if not re.search(r'[\W_]', value):  # Matches any non-alphanumeric character
        raise serializers.ValidationError(
            "Password must contain at least 1 special character.")

    return value


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=255,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            validate_username  # Custom validator for username
        ]
    )
    password = serializers.CharField(
        write_only=True,  # Do not expose the password in the response
        validators=[validate_password]  # Custom validator for password
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'password',
                  'status', 'role', 'created_at', 'updated_at']
        extra_kwargs = {
            'role': {'default': 'player'},  # Default role
        }

    def create(self, validated_data):
        # Hash the password before saving
        if 'password' in validated_data:
            validated_data['password'] = make_password(
                validated_data['password'])
        return super().create(validated_data)


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'status', 'role', 'updated_at']  # Include 'role'
        read_only_fields = ['updated_at']

    def update(self, instance, validated_data):
        # Update fields and save the instance
        instance.username = validated_data.get('username', instance.username)
        instance.status = validated_data.get('status', instance.status)
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance
