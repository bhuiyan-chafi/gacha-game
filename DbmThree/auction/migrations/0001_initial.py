# Generated by Django 4.2.16 on 2024-11-29 23:14

import auction.models
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, validators=[auction.models.validate_name])),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('banned', 'Banned'), ('Sold', 'sold'), ('10', 'Exchange Rate')], default='inactive', max_length=8)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'auction',
            },
        ),
        migrations.CreateModel(
            name='AuctionGachas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auction_id', models.BigIntegerField()),
                ('collection_id', models.BigIntegerField()),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0, message='Price cannot be negative.')])),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('banned', 'Banned'), ('Sold', 'sold'), ('10', 'Exchange Rate')], default='active', max_length=10)),
            ],
            options={
                'db_table': 'auction_gachas',
                'unique_together': {('auction_id', 'collection_id')},
            },
        ),
        migrations.CreateModel(
            name='AuctionGachaBid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auction_gacha_id', models.BigIntegerField()),
                ('bidder_id', models.BigIntegerField()),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0, message='Price must be a positive number.')])),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'auction_bids',
                'unique_together': {('auction_gacha_id', 'bidder_id', 'price')},
            },
        ),
    ]
