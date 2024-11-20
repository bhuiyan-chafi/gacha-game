from rest_framework import serializers
from .models import Gacha


class GachaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gacha
        fields = ['id', 'name', 'rarity', 'inventory',
                  'price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_inventory(self, value):
        """Ensure inventory is a non-negative integer"""
        if value < 0:
            raise serializers.ValidationError("Inventory cannot be negative.")
        return value

    def validate_price(self, value):
        """Ensure price is a non-negative integer"""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value
