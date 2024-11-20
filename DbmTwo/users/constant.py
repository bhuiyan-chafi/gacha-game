from django.db import models


class Status(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    BANNED = 'banned', 'Banned'
