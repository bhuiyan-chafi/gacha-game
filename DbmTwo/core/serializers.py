import re
from .helpers import decrypt_data
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Player, Admin

# Custom Validators


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


class PlayerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()  # Make it writable by default

    first_name = serializers.CharField(
        max_length=10, validators=[validate_name])
    last_name = serializers.CharField(
        max_length=10, validators=[validate_name])
    phone_number = serializers.CharField(
        max_length=10,
        validators=[
            validate_phone_number,
            UniqueValidator(
                queryset=Player.objects.all(),
                message="Phone number must be unique."
            )
        ]
    )
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
        read_only_fields = ['id']  # Only `id` is always read-only

    def validate_user_id(self, value):
        """
        Ensure user_id is unique across both Player and Admin models.
        """
        if Player.objects.filter(user_id=value).exists():
            raise serializers.ValidationError(
                "This user_id is already assigned to a player.")
        if Admin.objects.filter(user_id=value).exists():
            raise serializers.ValidationError(
                "This user_id is already assigned to an admin.")
        return value

    def update(self, instance, validated_data):
        # Prevent user_id from being updated
        validated_data.pop('user_id', None)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Customize the serialized output for the response."""
        representation = super().to_representation(instance)

        # Decrypt sensitive fields
        if representation.get('phone_number'):
            representation['phone_number'] = decrypt_data(
                representation['phone_number']
            )
        if representation.get('bank_details'):
            representation['bank_details'] = decrypt_data(
                representation['bank_details']
            )

        return representation


class AdminSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()  # Make it writable by default

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
        read_only_fields = ['id']  # Only `id` is always read-only

    def validate_user_id(self, value):
        """
        Ensure user_id is unique across both Player and Admin models.
        """
        if Player.objects.filter(user_id=value).exists():
            raise serializers.ValidationError(
                "This user_id is already assigned to a player.")
        if Admin.objects.filter(user_id=value).exists():
            raise serializers.ValidationError(
                "This user_id is already assigned to an admin.")
        return value

    def update(self, instance, validated_data):
        # Prevent user_id from being updated
        validated_data.pop('user_id', None)
        return super().update(instance, validated_data)
