from rest_framework import serializers
from .models import Gacha
import re


class GachaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gacha
        fields = ['id', 'name', 'rarity', 'inventory', 'price',
                  'description', 'image', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_description(self, value):
        """Ensure description does not exceed 150 characters."""
        if len(value) > 150:
            raise serializers.ValidationError(
                "Description must not exceed 150 characters."
            )
        return value

    def validate_image(self, value):
        """Ensure image name contains only alphanumeric characters."""
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise serializers.ValidationError(
                "Image name must contain only letters and numbers."
            )
        return value
