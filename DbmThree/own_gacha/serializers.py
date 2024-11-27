from rest_framework import serializers
from .models import PlayerGachaCollection


class PlayerGachaCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerGachaCollection
        fields = ['id', 'player_id', 'gacha_id', 'created_at']

    def validate(self, attrs):
        # Ensure the combination of player_id and gacha_id is unique
        if PlayerGachaCollection.objects.filter(player_id=attrs['player_id'], gacha_id=attrs['gacha_id']).exists():
            raise serializers.ValidationError(
                "This player and gacha combination already exists.")
        return attrs
