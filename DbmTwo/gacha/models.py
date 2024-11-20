from django.db import models
from django.utils import timezone
from users.constant import Status


class Gacha(models.Model):
    # Set unique=True to enforce uniqueness
    name = models.CharField(max_length=255, unique=True)
    rarity = models.IntegerField()
    inventory = models.IntegerField()
    price = models.IntegerField()
    status = models.CharField(
        max_length=8, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
