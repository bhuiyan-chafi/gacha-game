from django.db import models
from django.utils import timezone
from auth.constant import Status

# The following model: GachaUsers carries authentication information only. Personal details as a player or admin remains in separate databases.


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    # choices are defined in auth > constant.py
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(
        default=timezone.now)  # Default to current timestamp
    updated_at = models.DateTimeField(
        auto_now=True)  # Auto-updates on each save
