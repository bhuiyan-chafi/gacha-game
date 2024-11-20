from django.db import models
from django.utils.timezone import now  # Import timezone.now


class PlayerGachaCollection(models.Model):
    player_id = models.BigIntegerField()
    gacha_id = models.BigIntegerField()
    # Auto-assign current timestamp, not editable
    created_at = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'player_gacha_collection'  # Custom table name
        # Ensure no duplicate combinations
        unique_together = ('player_id', 'gacha_id')

    def __str__(self):
        return f"Player {self.player_id} - Gacha {self.gacha_id}"


class InGameCurrencyTransaction(models.Model):
    player_id = models.BigIntegerField()
    amount = models.FloatField()
    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = 'game_currency_transaction'

    def __str__(self):
        return f"Transaction for Player {self.player_id}: {self.amount}"
