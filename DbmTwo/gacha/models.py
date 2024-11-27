from django.db import models
from django.utils import timezone
from users.constant import Status


class Gacha(models.Model):
    # Set unique=True to enforce uniqueness
    name = models.CharField(max_length=255, unique=True)
    rarity = models.IntegerField()
    inventory = models.IntegerField()
    price = models.IntegerField()
    description = models.CharField(
        max_length=500, blank=False, null=False)  # New description field
    image = models.CharField(max_length=255, blank=False,
                             null=False)  # New image field
    status = models.CharField(
        max_length=8, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
