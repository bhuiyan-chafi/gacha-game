from django.db import models
from django.core.validators import RegexValidator, EmailValidator, MinValueValidator


class Player(models.Model):
    # Define validators for phone number and bank details
    phone_validator = RegexValidator(
        r'^\d+$', 'Phone number must contain only numbers.')
    bank_details_validator = RegexValidator(
        r'^[\w\s]+$', 'Bank details should not contain special characters.')

    user_id = models.BigIntegerField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email_address = models.EmailField(unique=True, validators=[
                                      EmailValidator(message="Enter a valid email address.")])
    phone_number = models.CharField(
        max_length=15, validators=[phone_validator])
    bank_details = models.CharField(
        max_length=255, validators=[bank_details_validator])
    current_balance = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(
            0.0, message="Balance cannot be negative.")]
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Admin(models.Model):
    phone_validator = RegexValidator(
        r'^\d+$', 'Phone number must contain only numbers.')

    user_id = models.BigIntegerField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email_address = models.EmailField(unique=True, validators=[
                                      EmailValidator(message="Enter a valid email address.")])
    phone_number = models.CharField(
        max_length=15, validators=[phone_validator])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
