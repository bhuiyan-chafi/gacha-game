from django.db import models
from django.utils import timezone
from dbm_three.constants import Status
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
import re


def validate_name(value):
    """
    Custom validator for the name field to ensure:
    - Name contains only alphanumeric characters and spaces.
    - Name does not exceed 20 characters.
    """
    if len(value) > 20:
        raise ValidationError("Name must not exceed 20 characters.")
    if not re.match(r'^[a-zA-Z0-9\s]+$', value):
        raise ValidationError(
            "Name must contain only letters, numbers, and spaces.")


class Auction(models.Model):
    name = models.CharField(
        # Django enforces max_length in forms, but we enforce it via the validator as well
        max_length=255,
        unique=True,
        validators=[validate_name]  # Custom validator using re
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(
        max_length=8, choices=Status.choices, default=Status.INACTIVE)
    created_at = models.DateTimeField(
        default=timezone.now)  # Current time on creation
    # Automatically updates on save
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'auction'  # Custom table name

    def __str__(self):
        return self.name


class AuctionGachas(models.Model):
    auction_id = models.BigIntegerField()
    collection_id = models.BigIntegerField()
    price = models.FloatField(validators=[
        MinValueValidator(0.0, message="Price cannot be negative.")
    ])
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    class Meta:
        db_table = 'auction_gachas'  # Custom table name
        # Ensure combination is unique
        unique_together = ('auction_id', 'collection_id')

    def __str__(self):
        return f"Auction {self.auction_id} - Collection {self.collection_id} ({self.status})"


class AuctionGachaBid(models.Model):
    auction_gacha_id = models.BigIntegerField()
    bidder_id = models.BigIntegerField()
    price = models.FloatField(
        validators=[
            MinValueValidator(0.0, message="Price must be a positive number.")
        ]
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'auction_bids'  # Custom table name
        unique_together = ('auction_gacha_id', 'bidder_id',
                           'price')  # Ensure combination is unique

    def __str__(self):
        return f"AuctionGachaID: {self.auction_gacha_id} - BidderID: {self.bidder_id} - Price: {self.price}"
