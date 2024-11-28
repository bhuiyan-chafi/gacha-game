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
        """
        Ensure image name contains only alphanumeric characters, underscores (_), and dots (.).
        """
        if not re.match(r'^[a-zA-Z0-9_.]+$', value):
            raise serializers.ValidationError(
                "Image name must contain only letters, numbers, underscores (_), and dots (.)."
            )
        return value

    def validate_rarity(self, value):
        """
        Ensure rarity is at least 10.
        """
        if value < 10:
            raise serializers.ValidationError(
                "Rarity must be at least 10."
            )
        return value
