from django.db import models


class SystemVariable(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Unique and not null
    value = models.TextField()  # String, not null

    class Meta:
        db_table = 'system_variable'  # Specify the table name for migrations
