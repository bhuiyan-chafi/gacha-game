# Generated by Django 4.2.16 on 2024-12-04 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='bank_details',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='phone_number',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]