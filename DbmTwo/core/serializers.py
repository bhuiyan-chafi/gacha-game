from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Player, Admin
import re

# Custom Validators


def validate_user_id(value):
    """
    Ensure user_id contains only numeric characters.
    """
    if not isinstance(value, int) or value < 0:
        raise serializers.ValidationError(
            "User ID must be a positive integer.")
    return value


def validate_name(value):
    """
    Ensure the name contains at most 10 characters.
    """
    if len(value) > 10:
        raise serializers.ValidationError(
            "Name must not exceed 10 characters.")
    if not value.isalpha():
        raise serializers.ValidationError("Name must contain only letters.")
    return value


def validate_phone_number(value):
    """
    Ensure the phone number contains only numeric characters.
    """
    if not re.match(r'^\d+$', value):
        raise serializers.ValidationError(
            "Phone number must contain only numbers.")
    return value


# Serializer for Player
class PlayerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(validators=[validate_user_id])
    first_name = serializers.CharField(
        max_length=10, validators=[validate_name])
    last_name = serializers.CharField(
        max_length=10, validators=[validate_name])
    phone_number = serializers.CharField(
        max_length=15, validators=[validate_phone_number])
    email_address = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=Player.objects.all(),
            message="Email address must be unique."
        )]
    )

    class Meta:
        model = Player
        fields = ['id', 'user_id', 'first_name', 'last_name', 'email_address',
                  'phone_number', 'bank_details', 'current_balance']


# Serializer for Admin
class AdminSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(validators=[validate_user_id])
    first_name = serializers.CharField(
        max_length=10, validators=[validate_name])
    last_name = serializers.CharField(
        max_length=10, validators=[validate_name])
    phone_number = serializers.CharField(
        max_length=15, validators=[validate_phone_number])
    email_address = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=Admin.objects.all(),
            message="Email address must be unique."
        )]
    )

    class Meta:
        model = Admin
        fields = ['id', 'user_id', 'first_name', 'last_name',
                  'email_address', 'phone_number']
