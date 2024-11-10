from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User
from rest_framework.validators import UniqueValidator

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=255,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    class Meta:
        model = User
        fields = ['username', 'password', 'status', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Hash the password before saving
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)