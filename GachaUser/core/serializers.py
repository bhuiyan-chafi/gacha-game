from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Player, Admin

# serializer for the player
class PlayerSerializer(serializers.ModelSerializer):
    email_address = serializers.EmailField(
        validators=[UniqueValidator(queryset=Player.objects.all(), message="Email address must be unique.")]
    )
    phone_number = serializers.CharField(
        max_length=15,
        validators=[UniqueValidator(queryset=Player.objects.all(), message="Phone number must be unique.")]
    )
    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'email_address', 'phone_number', 'bank_details', 'user_id']

# serializer for the admin
class AdminSerializer(serializers.ModelSerializer):
    email_address = serializers.EmailField(
        validators=[UniqueValidator(queryset=Admin.objects.all(), message="Email address must be unique.")]
    )
    phone_number = serializers.CharField(
        max_length=15,
        validators=[UniqueValidator(queryset=Admin.objects.all(), message="Phone number must be unique.")]
    )
    class Meta:
        model = Admin
        fields = ['id', 'first_name', 'last_name', 'email_address', 'phone_number', 'user_id']