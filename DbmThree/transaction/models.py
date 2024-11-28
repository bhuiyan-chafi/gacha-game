from django.db import models
from django.utils.timezone import now  # Import timezone.now
from django.core.exceptions import ValidationError


class InGameCurrencyTransaction(models.Model):
    player_id = models.BigIntegerField()
    amount = models.FloatField()
    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = 'game_currency_transaction'
