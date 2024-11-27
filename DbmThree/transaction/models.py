from django.db import models
from django.utils.timezone import now  # Import timezone.now
from django.core.exceptions import ValidationError


def validate_positive_amount(value):
    """
    Custom validator to ensure the amount is greater than 0.
    """
    if value <= 0:
        raise ValidationError("Amount must be greater than 0.")


class InGameCurrencyTransaction(models.Model):
    player_id = models.BigIntegerField()
    amount = models.FloatField(
        validators=[validate_positive_amount])  # Added validator
    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = 'game_currency_transaction'
