# Generated by Django 5.1.4 on 2025-01-20 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_alter_bid_bid'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='is_open',
            field=models.BooleanField(default=True),
        ),
    ]
