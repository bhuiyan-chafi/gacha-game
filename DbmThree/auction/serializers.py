from .models import AuctionGachaBid, AuctionGachas
from rest_framework import serializers
from .models import Auction


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ['id', 'name', 'start_date', 'end_date',
                  'status', 'created_at', 'updated_at']


class AuctionGachasSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionGachas
        fields = ['id', 'auction_id', 'collection_id', 'price', 'status']


class AuctionGachaBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionGachaBid
        fields = ['id', 'auction_gacha_id', 'bidder_id', 'price', 'created_at']

    def validate(self, data):
        # Validate price is higher than the current highest bid
        auction_gacha_id = data.get('auction_gacha_id')
        new_price = data.get('price')

        # Fetch the highest bid for this auction_gacha_id
        highest_bid = AuctionGachaBid.objects.filter(
            auction_gacha_id=auction_gacha_id
        ).order_by('-price').first()

        if highest_bid and new_price <= highest_bid.price:
            raise serializers.ValidationError({
                'price': f"Bid price must be greater than the current highest bid ({highest_bid.price})."
            })

        return data
