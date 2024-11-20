from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Player, Admin

# serializer for the player


class PlayerSerializer(serializers.ModelSerializer):
    email_address = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=Player.objects.all(), message="Email address must be unique.")]
    )
    phone_number = serializers.CharField(
        max_length=15,
        validators=[UniqueValidator(
            queryset=Player.objects.all(), message="Phone number must be unique.")]
    )
    # Define as a SerializerMethodField so that serializer understand the current_balance value should be expressed at two decimal points
    current_balance = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'email_address',
                  'phone_number', 'bank_details', 'user_id', 'current_balance']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure two decimal places as a float
        data['current_balance'] = round(float(data['current_balance']), 2)
        return data

# serializer for the admin


class AdminSerializer(serializers.ModelSerializer):
    email_address = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=Admin.objects.all(), message="Email address must be unique.")]
    )
    phone_number = serializers.CharField(
        max_length=15,
        validators=[UniqueValidator(
            queryset=Admin.objects.all(), message="Phone number must be unique.")]
    )

    class Meta:
        model = Admin
        fields = ['id', 'first_name', 'last_name',
                  'email_address', 'phone_number', 'user_id']
