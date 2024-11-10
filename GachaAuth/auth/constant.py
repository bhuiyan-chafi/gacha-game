from django.db import models
from django.utils import timezone

class Status(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    BANNED = 'banned', 'Banned'