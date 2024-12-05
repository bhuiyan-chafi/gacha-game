from django.db import models
from django.core.validators import RegexValidator, EmailValidator, MinValueValidator
from .helpers import encrypt_data, decrypt_data


class Player(models.Model):
    # Define validators for phone number and bank details
    phone_validator = RegexValidator(
        r'^\d+$', 'Phone number must contain only numbers.')
    bank_details_validator = RegexValidator(
        r'^[\w\s]+$', 'Bank details should not contain special characters.')

    user_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email_address = models.EmailField(unique=True, validators=[
                                      EmailValidator(message="Enter a valid email address.")])
    phone_number = models.CharField(unique=True,
                                    max_length=255)  # Encrypted, so allow longer length
    bank_details = models.CharField(
        max_length=255, unique=True)  # Encrypted, so allow longer length
    current_balance = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(
            0.0, message="Balance cannot be negative.")]
    )

    def save(self, *args, **kwargs):
        # print("Before saving: phone_number =",
        #       self.phone_number)  # Debug: Check value
        # print("Before saving: bank_details =",
        #       self.bank_details)  # Debug: Check value
        # # Encrypt sensitive fields before saving
        if self.phone_number and not self.phone_number.startswith('gAAAAA'):
            self.phone_number = encrypt_data(self.phone_number)
        if self.bank_details and not self.bank_details.startswith('gAAAAA'):
            self.bank_details = encrypt_data(self.bank_details)
        # print("After encryption: phone_number =",
        #       self.phone_number)  # Debug: Check encryption
        # print("After encryption: bank_details =",
        #       self.bank_details)  # Debug: Check encryption
        super().save(*args, **kwargs)

    @property
    def decrypted_phone_number(self):
        return decrypt_data(self.phone_number)

    @property
    def decrypted_bank_details(self):
        return decrypt_data(self.bank_details)


class Admin(models.Model):
    phone_validator = RegexValidator(
        r'^\d+$', 'Phone number must contain only numbers.')

    user_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email_address = models.EmailField(unique=True, validators=[
                                      EmailValidator(message="Enter a valid email address.")])
    phone_number = models.CharField(unique=True,
                                    max_length=15, validators=[phone_validator])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
