from django.db import models
from django.utils.timezone import now  # Import timezone.now
from django.core.exceptions import ValidationError


class PlayerGachaCollection(models.Model):
    player_id = models.BigIntegerField()
    gacha_id = models.BigIntegerField()
    # Auto-assign current timestamp, not editable
    created_at = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'player_gacha_collection'  # Custom table name
        # Ensure no duplicate combinations
        unique_together = ('player_id', 'gacha_id')
