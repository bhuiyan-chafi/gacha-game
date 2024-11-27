from rest_framework import serializers
from .models import InGameCurrencyTransaction


class InGameCurrencyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InGameCurrencyTransaction
        fields = ['id', 'player_id', 'amount', 'created_at']
